"""
=========================================================
BharatAI - Telegram Notification Service
=========================================================
"""

import logging
import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.services.telegram")
# Use existing logger configuration; avoid adding new handlers that may close unexpectedly.
# Ensure logger has at least a NullHandler to prevent 'No handler found' warnings.
if not logger.handlers:
    logger.addHandler(logging.NullHandler())

def send_telegram_message(message: str) -> bool:
    """Send a notification message to the configured Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram Bot Token or Chat ID not configured. Skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        logger.debug("Attempting to send Telegram notification...")
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.debug("Telegram notification sent successfully.")
            return True
        else:
            # If markdown parsing failed, retry with plain text
            logger.debug(f"Failed to send Telegram message with Markdown: {response.text}. Retrying as plain text...")
            payload.pop("parse_mode", None)
            try:
                response = requests.post(url, json=payload, timeout=10)
                if response.status_code == 200:
                    logger.debug("Telegram notification sent successfully (plain text fallback).")
                    return True
            except Exception as e:
                logger.debug(f"Telegram plain text send exception suppressed: {e}")
            
            logger.debug(f"Failed to send Telegram message: {response.text}")
            return False
    except Exception as e:
        logger.debug(f"Error sending Telegram message suppressed: {e}")
        return False
