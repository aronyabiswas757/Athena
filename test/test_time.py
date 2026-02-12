
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import engine, router
import datetime
from config import PREFERRED_MODEL

print("Testing Real-time Context...")

# Bypass validation (assume main.py holds the connection/server is up)
print("Using preferred model directly...")
engine.ACTIVE_MODEL_ID = PREFERRED_MODEL
print(f"Model: {engine.ACTIVE_MODEL_ID}")

# Test 1: Time Query
print("\n--- Test 1: What time is it? ---")
context_answer = engine.generate_answer_from_notes("What is the current time?")
print(f"Answer: {context_answer}")

# Test 2: Schedule Summary (Empty Future)
print("\n--- Test 2: Schedule Summary (Empty) ---")
# Mock data: A task in the past
past_time = (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
mock_data = f"- Call John at {past_time} (Completed)"
user_query = "Do I have any upcoming meetings?"

summary = engine.generate_summary(mock_data, user_query=user_query)
print(f"Summary: {summary}")
