"""
Actions Module: Executes OS-level actions like notifications.
"""
from plyer import notification
import logging

logger = logging.getLogger("athena")

def send_notification(title, message):
    """Sends a desktop notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="Athena",
            timeout=10
        )
        logger.info(f"Notification sent: {title} - {message}")
    except Exception as e:
        logger.error(f"Notification Error: {e}")
