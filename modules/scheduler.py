"""
Scheduler Module: Manages SQLite database operations for tasks.
"""
import sqlite3
import logging
from config import DB_PATH
from datetime import datetime

logger = logging.getLogger("athena")

def init_db():
    """Initializes the database schema."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending'
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database Initialization Error: {e}")
    finally:
        if conn:
            conn.close()

def add_task(task_name, execution_time):
    """Adds a new task to the schedule."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO schedule (task, time, status) VALUES (?, ?, ?)",
            (task_name, execution_time, 'pending')
        )
        conn.commit()
        logger.info(f"Task added: {task_name} at {execution_time}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Add Task Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_due_tasks(current_time=None):
    """Retrieves pending tasks that are due."""
    if current_time is None:
        current_time = datetime.now()
    
    # Format for string comparison in SQLite usually works best with close matching 
    # or by checking if time <= current_time for missed tasks
    # But strictly following spec: "SELECT * FROM schedule WHERE time = '10:20'" implies exact match logic or minute-level precision.
    # Let's use a range or minute truncation for robustness, but here I will implement "less than or equal to now" for robustness against slight delays.
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check for tasks that are pending and due (time <= current_time)
        cursor.execute(
            "SELECT * FROM schedule WHERE status = 'pending' AND time <= ?",
            (current_time,)
        )
        tasks = [dict(row) for row in cursor.fetchall()]
        return tasks
    except sqlite3.Error as e:
        logger.error(f"Get Tasks Error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_today_summary():
    """
    Returns a text block of today's tasks for the LLM to translate.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Select all tasks for today (simplification: all tasks in DB for now, or use date query)
        # For a "true" daily summary, we should filter by date. 
        # But given the inputs "in 20 minutes", they are today.
        
        start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        cursor.execute(
            "SELECT task, time, status FROM schedule WHERE time >= ? ORDER BY time ASC",
            (start_of_day,)
        )
        tasks = cursor.fetchall()
        
        if not tasks:
            return "No tasks scheduled for today."
            
        summary = "[DATA START]\n"
        for row in tasks:
            time_str = datetime.strptime(row['time'], '%Y-%m-%d %H:%M:%S.%f').strftime('%H:%M') if '.' in row['time'] else row['time']
            # formatting cleanup might be needed depending on how it was saved
            
            summary += f"- {time_str}: {row['task']} (Status: {row['status']})\n"
        summary += "[DATA END]"
        
        return summary
        
    except sqlite3.Error as e:
        logger.error(f"Summary Error: {e}")
        return "Error retrieving schedule."
    finally:
        if conn:
            conn.close()

def mark_task_complete(task_id):
    """Marks a task as completed/notified."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE schedule SET status = 'completed' WHERE id = ?",
            (task_id,)
        )
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Update Task Error: {e}")
    finally:
        if conn:
            conn.close()
