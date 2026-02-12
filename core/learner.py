"""
The Hippocampus: Handles Nightly Reflection and Profile Updates.
Reads interaction logs and updates the user profile with new insights.
"""
import json
import os
import sys
import requests

# Ensure we can import config.py from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LOG_DIR, LM_STUDIO_URL, LM_STUDIO_SETTINGS
from core.logger import log_decision, log_error

PROFILE_PATH = "data/profile.json"
INTERACTION_LOG = os.path.join(LOG_DIR, "interaction.log")

REFLECTION_PROMPT = """
Analyze the following interaction log.
Identify any NEW user preferences or facts.
Output a JSON object with the updated profile.
If no updates, return the current profile JSON.
Input Profile:
{current_profile}

Log:
{log_content}

Output JSON ONLY. No thinking. No markdown.
"""

def load_profile():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_profile(profile_data):
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile_data, f, indent=2)

def reflect():
    """
    Reads the full interaction log and attempts to update the profile.
    """
    log_decision("LEARNER", "SLEEP_CYCLE", "START", "Beginning reflection")
    
    if not os.path.exists(INTERACTION_LOG):
        log_decision("LEARNER", "SLEEP_CYCLE", "SKIP", "No logs found")
        return "No interaction log found."

    with open(INTERACTION_LOG, "r") as f:
        log_content = f.read()

    if not log_content.strip():
        return "Log is empty."

    current_profile = load_profile()
    
    # Construct Prompt
    prompt = REFLECTION_PROMPT.format(
        current_profile=json.dumps(current_profile, indent=2),
        log_content=log_content
    )

    from core import engine

    payload = {
        "model": engine.ACTIVE_MODEL_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        # Merge global settings
        **LM_STUDIO_SETTINGS
    }
    # Force lower temp for reflection
    payload["temperature"] = 0.1

    try:
        response = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload, timeout=300)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Robust JSON extraction
        import re
        
        # 1. Try to find markdown JSON block (Best Case) - Check this FIRST
        # Handles ```json and generic ``` blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, flags=re.DOTALL | re.IGNORECASE)
        
        if json_match:
            json_str = json_match.group(1)
        else:
            # 2. If no markdown, strip thought blocks to clean up garbage
            # Handle unclosed blocks (truncated output) by matching end-of-string '$'
            content = re.sub(r'<think>.*?(?:</think>|$)', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'\[THINK\].*?(?:\[/THINK\]|$)', '', content, flags=re.DOTALL | re.IGNORECASE)
            
            # 3. Fallback: Find first '{' and last '}'
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                json_str = content[start : end + 1]
            else:
                log_error("LEARNER", "No JSON found in reflection response")
                return "Reflection failed (No JSON)."

        try:
            new_profile = json.loads(json_str)
            save_profile(new_profile)
            log_decision("LEARNER", "SLEEP_CYCLE", "UPDATE", "Profile updated")
            return "Reflection complete."
        except json.JSONDecodeError as e:
            log_error("LEARNER", f"JSON Decode Error in Reflection: {e}")
            log_error("LEARNER", f"Failed JSON Content: {json_str[:100]}...") 
            return "Failed to parse reflection JSON."

    except Exception as e:
        log_error("LEARNER", f"Reflection Error: {e}")
        return f"Error during reflection: {e}"

    except Exception as e:
        log_error("LEARNER", f"Reflection Error: {e}")
        return f"Error during reflection: {e}"

if __name__ == "__main__":
    print(reflect())
