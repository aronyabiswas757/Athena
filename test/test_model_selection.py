
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import engine
from config import PREFERRED_MODELS

print("Testing Model Selection Logic...")
print(f"Preferred Models: {PREFERRED_MODELS}")

is_connected, model_id = engine.validate_model_connection()

if is_connected:
    print(f"SUCCESS: Connected to model '{model_id}'")
    if model_id in PREFERRED_MODELS:
        print(f"VERIFIED: Selected model is in preference list.")
    else:
        print(f"WARNING: Selected model is a fallback.")
else:
    print("FAILURE: Could not connect to LM Studio.")
