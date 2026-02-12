
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import engine
from config import PREFERRED_MODELS

print("Testing Model Selection Logic...")

print(f"Preferred Models: {PREFERRED_MODELS}")

is_connected, model_id, is_fallback = engine.validate_model_connection()

if is_connected:
    print(f"SUCCESS: Connected to model '{model_id}'")
    if not is_fallback:
        print(f"VERIFIED: Selected model is preferred (Lazy Match or Priority).")
    else:
        print(f"WARNING: Selected model is a fallback (Non-standard).")
else:
    print("FAILURE: Could not connect to LM Studio.")
