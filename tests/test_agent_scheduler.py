"""
=================================================
BharatAI - AgentScheduler Unit Tests
=================================================
"""

import time
import pytest

from core.event_bus import event_bus
from company.project_manager import ProjectManager
from company.agent_scheduler import AgentScheduler
from memory.memory_manager import memory_manager


def test_scheduler_enqueue_and_cancel():
    """Verify that jobs can be enqueued, retrieved, and cancelled."""
    memory_manager.clear_all()
    scheduler = AgentScheduler()

    job_id = scheduler.enqueue(
        project_id="proj_1",
        task_id="task_1",
        assigned_agent="developer",
        priority="Medium"
    )

    assert job_id is not None
    jobs = scheduler.get_queue_status()
    assert len(jobs) == 1
    assert jobs[0]["status"] == "Queued"
    assert jobs[0]["priority"] == "Medium"

    # Cancel job
    assert scheduler.cancel_job(job_id) is True
    assert scheduler.queue[job_id]["status"] == "Cancelled"

    # Dequeue
    assert scheduler.dequeue(job_id) is True
    assert len(scheduler.get_queue_status()) == 0


def test_scheduler_priority_queue_ordering():
    """Verify queue sorting prioritizes High -> Medium -> Low, then oldest first."""
    memory_manager.clear_all()
    scheduler = AgentScheduler()
    pm = ProjectManager()

    p_id = pm.create_project("Project Alpha", "Desc", "High", "ceo", "2026-12-31")
    t1 = pm.create_task(p_id, "Task 1", "Low Priority", "Low")
    t2 = pm.create_task(p_id, "Task 2", "High Priority", "High")
    t3 = pm.create_task(p_id, "Task 3", "Medium Priority", "Medium")

    # Enqueue in jumbled order
    j1 = scheduler.enqueue(p_id, t1, "developer", "Low")
    time.sleep(0.01) # ensure different timestamps
    j2 = scheduler.enqueue(p_id, t2, "developer", "High")
    time.sleep(0.01)
    j3 = scheduler.enqueue(p_id, t3, "developer", "Medium")

    # Dequeue/Assign next job: High priority first (j2)
    next_job = scheduler.assign_next_job(pm)
    assert next_job is not None
    assert next_job["id"] == j2
    assert next_job["status"] == "Running"

    # Dequeue/Assign next job: Medium priority next (j3)
    next_job2 = scheduler.assign_next_job(pm)
    assert next_job2 is not None
    assert next_job2["id"] == j3


def test_scheduler_dependencies():
    """Verify that tasks with unfulfilled dependencies are not scheduled."""
    memory_manager.clear_all()
    scheduler = AgentScheduler()
    pm = ProjectManager()

    p_id = pm.create_project("Project Dep", "Desc", "High", "ceo", "2026-12-31")
    t_parent = pm.create_task(p_id, "Parent Task", "Requirements", "High")
    # Dependent task: depends on t_parent
    t_child = pm.create_task(p_id, "Child Task", "Implementation", "High", dependencies=[t_parent])

    # Enqueue both
    job_child = scheduler.enqueue(p_id, t_child, "developer", "High")
    job_parent = scheduler.enqueue(p_id, t_parent, "developer", "High")

    # Attempt to assign: t_parent has no dependencies, so it should run.
    # t_child has dependent t_parent not completed, so it should NOT run first.
    assigned1 = scheduler.assign_next_job(pm)
    assert assigned1 is not None
    assert assigned1["task_id"] == t_parent  # Parent runs first

    # Try assigning again: child dependency not met (parent status is Running, not Completed)
    assigned2 = scheduler.assign_next_job(pm)
    assert assigned2 is None

    # Complete parent job
    scheduler.complete_job(job_parent, pm)

    # Now attempt to assign: child parent dependency met, so it should run.
    assigned3 = scheduler.assign_next_job(pm)
    assert assigned3 is not None
    assert assigned3["task_id"] == t_child


def test_scheduler_retry_logic():
    """Verify job retry increments retries and fails when limit is reached."""
    memory_manager.clear_all()
    scheduler = AgentScheduler()
    pm = ProjectManager()

    p_id = pm.create_project("Project Retry", "Desc", "Medium", "ceo", "2026-12-31")
    t_id = pm.create_task(p_id, "Test", "Desc", "Medium")
    j_id = scheduler.enqueue(p_id, t_id, "developer", "Medium")

    # Start
    scheduler.assign_next_job(pm)
    
    # Fail once: retry (should re-queue)
    assert scheduler.retry_job(j_id, max_retries=2) is True
    assert scheduler.queue[j_id]["status"] == "Queued"
    assert scheduler.queue[j_id]["retries"] == 1

    # Start and fail twice: exceeds max_retries=2
    scheduler.assign_next_job(pm)
    assert scheduler.retry_job(j_id, max_retries=2) is False
    assert scheduler.queue[j_id]["status"] == "Failed"
    assert scheduler.queue[j_id]["retries"] == 2


def test_scheduler_persistence_recovery():
    """Verify that queue state is persisted and successfully recovered upon restart."""
    memory_manager.clear_all()
    scheduler1 = AgentScheduler()

    j_id = scheduler1.enqueue("p_1", "t_1", "developer", "High")

    # Re-instantiate
    scheduler2 = AgentScheduler()
    assert j_id in scheduler2.queue
    assert scheduler2.queue[j_id]["priority"] == "High"


def test_stuck_jobs_detection():
    """Verify that stuck jobs are correctly identified based on timeout thresholds."""
    memory_manager.clear_all()
    scheduler = AgentScheduler()

    j1 = scheduler.enqueue("p_1", "t_1", "developer", "High")
    j2 = scheduler.enqueue("p_1", "t_2", "qa", "High")

    # Mark j1 running, started 100 seconds ago
    scheduler.queue[j1]["status"] = "Running"
    scheduler.queue[j1]["started_at"] = time.time() - 100.0

    # Mark j2 running, started 10 seconds ago
    scheduler.queue[j2]["status"] = "Running"
    scheduler.queue[j2]["started_at"] = time.time() - 10.0

    # Detect stuck jobs with 30 seconds timeout: j1 should be detected, j2 not
    stuck = scheduler.detect_stuck_jobs(timeout_seconds=30.0)
    assert j1 in stuck
    assert j2 not in stuck
