"""
Monitor Module ("The Heart"): Background event loop for checking schedules.
"""
import time
import threading
import logging
from modules import scheduler, actions, voice
from config import POLL_INTERVAL_SECONDS
from core.logger import log_decision, log_error

# logger = logging.getLogger("athena") # Removed in favor of structured logger

# State Machine definitions
class State:
    IDLE = "IDLE"
    DEEP_WORK = "DEEP_WORK"
    DO_NOT_DISTURB = "DO_NOT_DISTURB"

CURRENT_STATE = State.IDLE

def set_state(new_state):
    global CURRENT_STATE
    if new_state in [State.IDLE, State.DEEP_WORK, State.DO_NOT_DISTURB]:
        old_state = CURRENT_STATE
        CURRENT_STATE = new_state
        log_decision("MONITOR", "STATE_CHANGE", "UPDATE", f"{old_state} -> {CURRENT_STATE}")
        return True
    return False

class Monitor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True # Daemon thread dies when main program exits
        self.stop_event = threading.Event()

    def run(self):
        log_decision("MONITOR", "STARTUP", "INIT", "Heartbeat started")
        while not self.stop_event.is_set():
            try:
                self.check_schedule()
            except Exception as e:
                log_error("MONITOR", f"Loop Error: {e}")
            
            # Wait for interval or until stopped
            self.stop_event.wait(POLL_INTERVAL_SECONDS)

    def check_schedule(self):
        """Checks for tasks due now."""
        # Query tasks
        due_tasks = scheduler.get_due_tasks()
        
        for task in due_tasks:
            task_name = task['task']
            task_id = task['id']
            
            log_decision("MONITOR", CURRENT_STATE, "TRIGGER_ATTEMPT", f"Task Due: {task_name}")
            
            # State-based logic
            if CURRENT_STATE == State.DO_NOT_DISTURB:
                log_decision("MONITOR", CURRENT_STATE, "ACTION_SUPPRESSED", "DND matches, silencing all")
                # We still mark as complete so it doesn't loop forever? 
                # Or maybe we shouldn't mark complete? 
                # For simplicity in this version, we suppress notification but mark complete to avoid pile-up.
                # Ideally, we should "snooze" it.
                pass 
                
            elif CURRENT_STATE == State.DEEP_WORK:
                # Soft notify (Log only, maybe visual if we had a GUI)
                log_decision("MONITOR", CURRENT_STATE, "AUDIO_SUPPRESSED", "Deep Work active")
                actions.send_notification("Athena (Silent)", f"Missed: {task_name}")
                
            else:
                # IDLE / Normal
                actions.send_notification("Athena Reminder", task_name)
                voice.speak(f"Reminder: {task_name}")
            
            # Mark complete
            scheduler.mark_task_complete(task_id)

    def stop(self):
        self.stop_event.set()
