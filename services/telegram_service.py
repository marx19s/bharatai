"""
=================================================
BharatAI - Telegram Executive Notification Service
=================================================
"""

import os
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

import requests
from core.event_bus import event_bus

logger = logging.getLogger("bharatai.services.telegram")


class TelegramService:
    """
    Asynchronous, non-blocking Telegram notification service for BharatAI.
    Subscribes to project and task lifecycle events and issues executive alerts.
    """

    def __init__(self):
        self.bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        self.enabled = os.environ.get("ENABLE_TELEGRAM", "false").lower() == "true"
        
        # Non-blocking async dispatch pool
        self.executor = ThreadPoolExecutor(max_workers=1)
        self._setup_event_subscriptions()

    def test_connection(self) -> bool:
        """Validate credentials and test connection to the Telegram API."""
        if not self.bot_token or not self.chat_id:
            logger.warning("TelegramService: Missing bot token or chat ID.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("TelegramService: Connection validation successful.")
                return True
            else:
                logger.error(f"TelegramService: Validation failed with status {response.status_code}.")
                return False
        except Exception as e:
            logger.error(f"TelegramService: Connection test threw exception: {e}")
            return False

    def _setup_event_subscriptions(self) -> None:
        """Subscribe notification handlers to project and task EventBus events."""
        event_bus.subscribe("ProjectCreated", self.on_project_created)
        event_bus.subscribe("ProjectCompleted", self.on_project_completed)
        event_bus.subscribe("JobStarted", self.on_job_started)
        event_bus.subscribe("JobCompleted", self.on_job_completed)
        event_bus.subscribe("JobFailed", self.on_job_failed)
        event_bus.subscribe("ExecutionCompleted", self.on_execution_completed)
        event_bus.subscribe("ExecutionFailed", self.on_execution_failed)

    def _send_post_request(self, text: str) -> None:
        """Issue message payload to Telegram API. Handles retries and timeouts gracefully."""
        if not self.enabled:
            return
        if not self.bot_token or not self.chat_id:
            logger.debug("TelegramService: Telegram notifications are enqueued but service parameters are unset.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = requests.post(url, json=payload, timeout=5)
                if response.status_code == 200:
                    logger.debug("TelegramService: Message sent successfully.")
                    return
                else:
                    logger.warning(f"TelegramService: API returned status {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"TelegramService: Attempt {attempt+1} failed with exception: {e}")

        logger.error("TelegramService: Notification message delivery failed after max retries.")

    def send_message(self, text: str) -> None:
        """Queue a raw notification message to be sent asynchronously."""
        self.executor.submit(self._send_post_request, text)

    def send_error(self, text: str) -> None:
        """Queue an error notification alert."""
        self.send_message(f"❌ <b>[ERROR]</b> {text}")

    def send_success(self, text: str) -> None:
        """Queue a success notification alert."""
        self.send_message(f"✅ <b>[SUCCESS]</b> {text}")

    def send_warning(self, text: str) -> None:
        """Queue a warning notification alert."""
        self.send_message(f"⚠️ <b>[WARNING]</b> {text}")

    def send_daily_summary(self, summary_data: Dict[str, Any]) -> None:
        """Queue a structured daily executive report notification."""
        report = (
            "🚀 <b>BharatAI Report</b>\n\n"
            f"<b>Project:</b>\n{summary_data.get('project', 'N/A')}\n\n"
            f"<b>Completed:</b>\n{summary_data.get('completed', 0)}\n\n"
            f"<b>Failed:</b>\n{summary_data.get('failed', 0)}\n\n"
            f"<b>Active Agents:</b>\n{summary_data.get('active_agents', 0)}\n\n"
            f"<b>Queue:</b>\n{summary_data.get('queue', 0)}\n\n"
            f"<b>Duration:</b>\n{summary_data.get('duration', 'N/A')}"
        )
        self.send_message(report)

    # ==========================================
    # EventBus Event Handlers
    # ==========================================

    def on_project_created(self, event) -> None:
        payload = event.payload
        msg = (
            "🚀 <b>New Project Created</b>\n"
            f"<b>ID:</b> {payload.get('project_id')}\n"
            f"<b>Name:</b> {payload.get('name')}\n"
            f"<b>Owner:</b> {payload.get('owner')}"
        )
        self.send_message(msg)

    def on_project_completed(self, event) -> None:
        payload = event.payload
        msg = (
            "🎉 <b>Project Completed</b>\n"
            f"<b>ID:</b> {payload.get('project_id')}\n"
            f"<b>Name:</b> {payload.get('name')}"
        )
        self.send_success(msg)

    def on_job_started(self, event) -> None:
        payload = event.payload
        msg = (
            "🏃 <b>Task Workload Started</b>\n"
            f"<b>Job ID:</b> {payload.get('job_id')}\n"
            f"<b>Task ID:</b> {payload.get('task_id')}\n"
            f"<b>Agent Assigned:</b> {payload.get('assigned_agent')}"
        )
        self.send_message(msg)

    def on_job_completed(self, event) -> None:
        payload = event.payload
        msg = (
            "💪 <b>Task Workload Completed</b>\n"
            f"<b>Job ID:</b> {payload.get('job_id')}\n"
            f"<b>Task ID:</b> {payload.get('task_id')}"
        )
        self.send_success(msg)

    def on_job_failed(self, event) -> None:
        payload = event.payload
        msg = (
            "⚠️ <b>Task Workload Failed</b>\n"
            f"<b>Job ID:</b> {payload.get('job_id')}\n"
            f"<b>Task ID:</b> {payload.get('task_id')}\n"
            f"<b>Error:</b> {payload.get('error')}"
        )
        self.send_error(msg)

    def on_execution_completed(self, event) -> None:
        payload = event.payload
        msg = (
            "🔥 <b>Autonomous Loop Completed</b>\n"
            f"<b>Project ID:</b> {payload.get('project_id')}"
        )
        self.send_success(msg)

    def on_execution_failed(self, event) -> None:
        payload = event.payload
        msg = (
            "🚨 <b>Autonomous Loop Execution Failed</b>\n"
            f"<b>Project ID:</b> {payload.get('project_id')}\n"
            f"<b>Error:</b> {payload.get('error')}"
        )
        self.send_error(msg)

    def shutdown(self) -> None:
        """Shutdown the executor pool cleanly and unsubscribe from EventBus."""
        self.executor.shutdown(wait=True)
        try:
            event_bus.unsubscribe("ProjectCreated", self.on_project_created)
            event_bus.unsubscribe("ProjectCompleted", self.on_project_completed)
            event_bus.unsubscribe("JobStarted", self.on_job_started)
            event_bus.unsubscribe("JobCompleted", self.on_job_completed)
            event_bus.unsubscribe("JobFailed", self.on_job_failed)
            event_bus.unsubscribe("ExecutionCompleted", self.on_execution_completed)
            event_bus.unsubscribe("ExecutionFailed", self.on_execution_failed)
        except Exception as e:
            logger.debug(f"TelegramService: Unsubscribe failed: {e}")
