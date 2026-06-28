"""
=================================================
BharatAI - TelegramService Unit Tests
=================================================
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from core.event_bus import event_bus
from services.telegram_service import TelegramService


@pytest.fixture
def mock_env(monkeypatch):
    """Setup test credentials and toggle notification sending on."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u1")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-987654321")
    monkeypatch.setenv("ENABLE_TELEGRAM", "true")


def test_telegram_connection_success(mock_env):
    """Verify test_connection returns True when API returns 200."""
    service = TelegramService()
    
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        assert service.test_connection() is True
        mock_get.assert_called_once()
    service.shutdown()


def test_telegram_connection_failure(mock_env):
    """Verify test_connection returns False when API errors out."""
    service = TelegramService()

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 401
        assert service.test_connection() is False
    service.shutdown()


def test_telegram_send_message_non_blocking(mock_env):
    """Verify that send_message queues task asynchronously without blocking caller."""
    service = TelegramService()
    
    with patch("requests.post") as mock_post:
        # Simulate slow response
        def slow_post(*args, **kwargs):
            time.sleep(0.1)
            mock_res = MagicMock()
            mock_res.status_code = 200
            return mock_res

        mock_post.side_effect = slow_post

        start_time = time.time()
        service.send_message("Testing non-blocking")
        elapsed = time.time() - start_time
        
        # Must return immediately, well under 0.1 seconds sleep threshold
        assert elapsed < 0.05

        # Cleanup executor pool
        service.shutdown()
        assert mock_post.call_count == 1


def test_telegram_retry_logic(mock_env):
    """Verify request retry attempts cap at max 3 retries on request failure."""
    service = TelegramService()

    with patch("requests.post") as mock_post:
        # Cause exception to trigger retry path
        mock_post.side_effect = Exception("Network timeout")

        service.send_message("Should fail after 3 attempts")
        service.shutdown()

        # Should attempt 3 times
        assert mock_post.call_count == 3


def test_telegram_notification_formatting(mock_env):
    """Verify that send alerts construct correct HTML tags."""
    service = TelegramService()

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        service.send_success("Done")
        service.send_error("Fail")
        service.send_warning("Careful")
        
        service.shutdown()

        calls = mock_post.call_args_list
        assert len(calls) == 3
        
        # Verify formats
        assert "✅ <b>[SUCCESS]</b> Done" in calls[0].kwargs["json"]["text"]
        assert "❌ <b>[ERROR]</b> Fail" in calls[1].kwargs["json"]["text"]
        assert "⚠️ <b>[WARNING]</b> Careful" in calls[2].kwargs["json"]["text"]


def test_telegram_event_bus_integration(mock_env):
    """Verify TelegramService listens to EventBus events and posts corresponding notifications."""
    service = TelegramService()

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        # Publish task completed event
        event_bus.publish("ProjectCreated", "test", {
            "project_id": "p123",
            "name": "YAAR AI",
            "owner": "ceo"
        })

        # Allow async executor worker thread to pick up and run the job
        service.shutdown()

        assert mock_post.call_count == 1
        sent_text = mock_post.call_args.kwargs["json"]["text"]
        assert "🚀 <b>New Project Created</b>" in sent_text
        assert "YAAR AI" in sent_text
