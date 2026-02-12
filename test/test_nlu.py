
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import engine

from config import PREFERRED_MODEL

# Initialize Engine State
engine.ACTIVE_MODEL_ID = PREFERRED_MODEL
print(f"Using Model: {engine.ACTIVE_MODEL_ID}")

test_input = "I prefer all time in 12 hour Format"
print(f"Testing input: '{test_input}'")

result = engine.process_input(test_input)
print("Result:", result)
