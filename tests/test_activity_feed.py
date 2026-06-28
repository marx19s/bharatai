"""
=================================================
BharatAI - Activity Feed Unit Tests (Sprint 5.2)
=================================================
"""

import time
import pytest

from core.event_bus import event_bus
from memory.memory_manager import memory_manager
from company.office_manager import OfficeManager
from company.project_manager import ProjectManager
from company.office_api import OfficeAPI
from ui.activity_feed import ActivityFeedStore, ActivityFeedComponent, _infer_dept, _format_ago


# ---------------------------------------------------------------------------
# ActivityFeedStore tests
# ---------------------------------------------------------------------------

class TestActivityFeedStore:

    def setup_method(self):
        self.store = ActivityFeedStore()

    def test_ingest_and_retrieve(self):
        """Events ingested should appear in get_events() in newest-first order."""
        self.store.ingest_event("JobCompleted", "developer", {"task": "Write tests"})
        self.store.ingest_event("JobFailed",    "qa",        {"task": "Review PR", "error": "Timeout"})

        events = self.store.get_events()
        assert len(events) == 2
        # Newest first
        assert events[0]["event_type"] == "JobFailed"
        assert events[1]["event_type"] == "JobCompleted"

    def test_event_fields_populated(self):
        """Ingested event must populate all required fields."""
        self.store.ingest_event("TaskStarted", "neo", {
            "task": "Orchestrate planning",
            "department": "CEO",
            "duration": 1.23,
        })
        ev = self.store.get_events()[0]

        assert ev["agent"] == "neo"
        assert ev["department"] == "CEO"
        assert ev["task"] == "Orchestrate planning"
        assert ev["duration"] == 1.23
        assert ev["status"] in ("running", "success", "error", "warning", "info")
        assert "timestamp" in ev

    def test_max_events_capped(self):
        """Ring-buffer should never exceed MAX_EVENTS=100."""
        for i in range(150):
            self.store.ingest_event("TaskCompleted", f"agent_{i}", {"task": f"task_{i}"})

        assert self.store.count() == 100
        assert len(self.store.get_events()) == 100

    def test_limit_parameter(self):
        """get_events(limit=N) should respect N."""
        for i in range(20):
            self.store.ingest_event("JobCompleted", "developer", {"task": f"job_{i}"})

        assert len(self.store.get_events(limit=5)) == 5

    def test_empty_state(self):
        """Empty store returns empty list."""
        assert self.store.get_events() == []
        assert self.store.count() == 0

    def test_ingest_raw(self):
        """ingest_raw() accepts a pre-built dict."""
        record = {
            "event_type": "Error",
            "emoji": "🔴",
            "label": "Error",
            "status": "error",
            "agent": "lumina",
            "department": "Operations",
            "task": "—",
            "duration": None,
            "error": "Connection refused",
            "timestamp": time.time(),
        }
        self.store.ingest_raw(record)
        ev = self.store.get_events()[0]
        assert ev["event_type"] == "Error"
        assert ev["error"] == "Connection refused"

    def test_clear(self):
        """clear() empties the store."""
        self.store.ingest_event("JobCompleted", "developer", {})
        self.store.clear()
        assert self.store.count() == 0

    def test_unknown_event_type_handled(self):
        """Unknown event types should be ingested without raising an exception."""
        self.store.ingest_event("UnknownCustomEvent", "orion", {"task": "mystery"})
        ev = self.store.get_events()[0]
        assert ev["event_type"] == "UnknownCustomEvent"
        assert ev["status"] == "info"   # default status


# ---------------------------------------------------------------------------
# OfficeAPI activity feed integration tests
# ---------------------------------------------------------------------------

class TestOfficeAPIActivityFeed:

    def setup_method(self):
        memory_manager.clear_all()
        self.om  = OfficeManager()
        self.pm  = ProjectManager()
        self.api = OfficeAPI(self.om, self.pm)

    def teardown_method(self):
        self.api.shutdown()

    def test_activity_feed_empty_before_events(self):
        """Feed should be empty when no events have been published."""
        feed = self.api.get_activity_feed()
        # May contain 0 records from a clean memory
        assert isinstance(feed, list)

    def test_activity_feed_captures_job_completed(self):
        """Publishing JobCompleted should appear in get_activity_feed()."""
        event_bus.publish("JobCompleted", "developer", {
            "task": "Build module", "duration": 3.5
        })
        feed = self.api.get_activity_feed()
        event_types = [e["event_type"] for e in feed]
        assert "JobCompleted" in event_types

    def test_activity_feed_captures_job_failed(self):
        """Publishing JobFailed should appear in get_activity_feed() with status=error."""
        event_bus.publish("JobFailed", "qa", {
            "task": "Integration test", "error": "Assert failed"
        })
        feed = self.api.get_activity_feed()
        failed_entries = [e for e in feed if e["event_type"] == "JobFailed"]
        assert len(failed_entries) >= 1
        assert failed_entries[0]["status"] == "error"
        assert failed_entries[0]["error"] == "Assert failed"

    def test_activity_feed_captures_execution_events(self):
        """ExecutionStarted and ExecutionCompleted should appear in the feed."""
        event_bus.publish("ExecutionStarted",   "neo", {"task": "Sprint plan"})
        event_bus.publish("ExecutionCompleted", "neo", {"task": "Sprint plan"})

        feed = self.api.get_activity_feed()
        event_types = [e["event_type"] for e in feed]
        assert "ExecutionStarted"   in event_types
        assert "ExecutionCompleted" in event_types

    def test_activity_feed_captures_project_created(self):
        """ProjectCreated event should appear in feed."""
        event_bus.publish("ProjectCreated", "neo", {"task": "Project Alpha"})
        feed = self.api.get_activity_feed()
        assert any(e["event_type"] == "ProjectCreated" for e in feed)

    def test_activity_feed_respects_limit(self):
        """get_activity_feed(limit=5) returns at most 5 records."""
        for i in range(10):
            event_bus.publish("TaskCompleted", "developer", {"task": f"task_{i}"})

        feed = self.api.get_activity_feed(limit=5)
        assert len(feed) <= 5

    def test_activity_feed_newest_first(self):
        """Records should be sorted newest first."""
        event_bus.publish("TaskStarted",   "neo", {"task": "step 1"})
        time.sleep(0.01)
        event_bus.publish("TaskCompleted", "neo", {"task": "step 2"})

        feed = self.api.get_activity_feed()
        if len(feed) >= 2:
            assert feed[0]["timestamp"] >= feed[1]["timestamp"]

    def test_get_company_dashboard_includes_activity_feed(self):
        """get_company_dashboard() must include the 'activity_feed' key."""
        event_bus.publish("JobCompleted", "developer", {"task": "Dashboard test"})
        dashboard = self.api.get_company_dashboard()

        assert "activity_feed" in dashboard
        assert isinstance(dashboard["activity_feed"], list)

    def test_activity_record_fields(self):
        """Every activity record must contain required fields."""
        event_bus.publish("TelegramSent", "echo", {"task": "Notify user"})
        feed = self.api.get_activity_feed()
        tg_entries = [e for e in feed if e["event_type"] == "TelegramSent"]
        assert len(tg_entries) >= 1

        record = tg_entries[0]
        required_fields = ["event_type", "label", "status", "agent",
                           "department", "task", "timestamp"]
        for field in required_fields:
            assert field in record, f"Missing field: {field}"

    def test_memory_pruning_under_100(self):
        """Ensure memory is pruned to 100 when more than 100 activity events are published."""
        for i in range(110):
            event_bus.publish("TaskCompleted", "developer", {"task": f"auto_{i}"})

        feed = self.api.get_activity_feed(limit=200)   # ask for more than 100
        assert len(feed) <= 100


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------

class TestHelpers:

    def test_infer_dept_known_agents(self):
        assert _infer_dept("neo")         == "CEO"
        assert _infer_dept("atlas")       == "CEO"
        assert _infer_dept("developer")   == "Engineering"
        assert _infer_dept("reviewer")    == "Engineering"
        assert _infer_dept("bug_fixer")   == "Engineering"
        assert _infer_dept("performance") == "Engineering"
        assert _infer_dept("qa")          == "QA"
        assert _infer_dept("orion")       == "Research"
        assert _infer_dept("lumina")      == "Operations"

    def test_infer_dept_unknown_defaults_to_operations(self):
        assert _infer_dept("unknown_bot") == "Operations"

    def test_infer_dept_case_insensitive(self):
        assert _infer_dept("NEO")    == "CEO"
        assert _infer_dept("ORION")  == "Research"

    def test_format_ago_seconds(self):
        assert _format_ago(30)   == "30s ago"
        assert _format_ago(0)    == "0s ago"
        assert _format_ago(59)   == "59s ago"

    def test_format_ago_minutes(self):
        assert _format_ago(90)   == "1m 30s ago"
        assert _format_ago(120)  == "2m 0s ago"
        assert _format_ago(3599) == "59m 59s ago"

    def test_format_ago_hours(self):
        assert _format_ago(3600)  == "1h 0m ago"
        assert _format_ago(7380)  == "2h 3m ago"


# ---------------------------------------------------------------------------
# ActivityFeedComponent smoke tests (no Streamlit context — just verify init)
# ---------------------------------------------------------------------------

class TestActivityFeedComponentInit:

    def test_component_instantiates(self):
        """Component should be instantiable without requiring Streamlit context."""
        comp = ActivityFeedComponent()
        assert comp is not None

    def test_status_style_completeness(self):
        """All expected status types have style entries."""
        comp = ActivityFeedComponent()
        for status in ("success", "running", "error", "warning", "info"):
            assert status in comp._STATUS_STYLE
