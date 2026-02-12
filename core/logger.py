"""
Structured Logger: Provides a rigid format for observability.
Format: [COMPONENT] STATE -> ACTION: RESULT
"""
import logging
import os
from config import LOG_DIR

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure Main Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "decision_trace.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("athena")

def log_decision(component, state, action, result):
    """
    Logs a structured decision trace.
    Example: log_decision("MONITOR", "IDLE", "CHECK_SCHEDULE", "0 Tasks Found")
    """
    message = f"[{component.upper()}] {state} -> {action}: {result}"
    logger.info(message)

def safe_log(message):
    """
    Safely logs a message, handling Unicode errors for console output.
    """
    try:
        logger.info(message)
    except:
        # Fallback for Windows console encoding issues
        try:
            clean_msg = message.encode('ascii', 'replace').decode('ascii')
            logger.info(clean_msg)
        except:
            pass

def log_error(component, error_msg):
    """Logs an error with the component context."""
    # Use safe logging for errors too, as they might contain weird characters
    try:
        logger.error(f"[{component.upper()}] ERROR: {error_msg}")
    except:
         logger.error(f"[{component.upper()}] ERROR: {error_msg}".encode('ascii', 'replace').decode('ascii'))

# Configure Conversation Logger
# This logger captures the raw dialogue for the Learner ("Hippocampus") to analyze.
conversation_logger = logging.getLogger("athena_conversation")
conversation_logger.setLevel(logging.INFO)
conv_handler = logging.FileHandler(os.path.join(LOG_DIR, "interaction.log"), encoding='utf-8')
conv_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
conversation_logger.addHandler(conv_handler)

def log_interaction(user_text, athena_text):
    """
    Logs the user input and Athena's response.
    Format:
    User: [text]
    Athena: [text]
    """
    # Write to file (utf-8 safe)
    conversation_logger.info(f"User: {user_text}")
    conversation_logger.info(f"Athena: {athena_text}")
