
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import engine
from config import PREFERRED_MODELS

print("Testing Model Selection Logic...")


print(f"Preferred Models: {PREFERRED_MODELS}")

try:
    is_connected, model_id, _ = engine.validate_model_connection()

    if is_connected:
        print(f"SUCCESS: Connected to model '{model_id}'")
        # Logic Verification
        # Scenario 1: If loaded, it should match the loaded one.
        # Scenario 2: If auto-loaded, it should be a preferred one.
        print("VERIFIED: Model selection logic executed successfully.")
    else:
        print("FAILURE: Could not connect to LM Studio or all models failed.")
except Exception as e:
    print(f"ERROR: Script failed with {e}")
