"""
Core Engine: Handles NLU and Intent Classification using LM Studio.
"""
import requests
import json
import logging
from .prompts import SCHEDULER_PROMPT
from config import LM_STUDIO_URL, LM_STUDIO_SETTINGS, PREFERRED_MODELS, PREFERRED_MODEL
from core.logger import log_decision, log_error

# logger = logging.getLogger("athena")

ACTIVE_MODEL_ID = None

def validate_model_connection():
    """
    Checks if LM Studio is running and selects the best available model.
    Logic:
    1. Scenario 1: If ANY model is already loaded, use it (Irrespective of config).
    2. Scenario 2 & 3: If NO model is loaded, iterate PREFERRED_MODELS and try to "Force Open" (Active Probe).
    3. Scenario 4: If all fail, abort.
    
    Returns: (is_connected, model_id, is_fallback)
    """
    global ACTIVE_MODEL_ID
    
    try:
        # Step 1: Check what is currently loaded
        try:
            response = requests.get(f"{LM_STUDIO_URL}/models", timeout=5)
        except requests.exceptions.ConnectionError:
            log_decision("ENGINE", "STARTUP", "CONN_FAIL", "Could not connect to LM Studio (Server Down).")
            return False, None, False

        if response.status_code != 200:
            return False, None, False
            
        data = response.json()
        loaded_models = data.get('data', [])
        
        # Scenario 1: An LLM is already loaded. Use it.
        if loaded_models:
            active_model = loaded_models[0]['id']
            log_decision("ENGINE", "STARTUP", "MODEL_FOUND", f"Using loaded model: {active_model}")
            ACTIVE_MODEL_ID = active_model
            # Treat as valid (is_fallback=False) to suppress warnings, per user "Use it" instruction.
            return True, active_model, False
            
        # Scenario 2 & 3: No LLM loaded. Force open priority list.
        log_decision("ENGINE", "STARTUP", "MODEL_AUTO", "No models loaded. Attempting Active Probe sequence...")
        
        for priority_model in PREFERRED_MODELS:
            print(f"Attempting to load priority model: {priority_model}...")
            
            # Active Probe: Send a tiny dummy request to force JIT loading
            probe_payload = {
                "model": priority_model,
                "messages": [{"role": "user", "content": "ping"}],
                "max_tokens": 1
            }
            
            try:
                # Long timeout to allow for JIT loading (Model Load could take time)
                # LM Studio usually handles the load and then responds.
                probe_response = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=probe_payload, timeout=30)
                
                if probe_response.status_code == 200:
                    log_decision("ENGINE", "STARTUP", "MODEL_LOADED", f"Successfully loaded: {priority_model}")
                    ACTIVE_MODEL_ID = priority_model
                    return True, priority_model, False
                else:
                    log_decision("ENGINE", "STARTUP", "MODEL_FAIL", f"Failed to load {priority_model}: {probe_response.status_code}")
                    continue # Try next model
                    
            except requests.exceptions.RequestException as e:
                 log_decision("ENGINE", "STARTUP", "MODEL_ERR", f"Error loading {priority_model}: {e}")
                 continue # Try next model

        # Scenario 4: No LLM loaded or available (All probes failed)
        log_error("ENGINE", "All preferred models failed to load.")
        return False, None, False

    except Exception as e:
        log_error("ENGINE", f"Model Validation Failed: {e}")
        return False, None, False
def process_input(user_text, model_id=None):
    """
    Sends user text to the LLM and returns structured JSON.
    """
    # Load User Profile
    system_prompt = SCHEDULER_PROMPT
    try:
        with open("data/profile.json", "r") as f:
            profile = f.read()
            system_prompt += f"\n\nUser Profile (The Constitution):\n{profile}\n"
    except Exception:
        pass # Fail silently if profile doesn't exist yet

    payload = {
        "model": ACTIVE_MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        **LM_STUDIO_SETTINGS
    }
    
    try:
        response = requests.post(
            f"{LM_STUDIO_URL}/chat/completions", 
            json=payload,
            timeout=LM_STUDIO_SETTINGS["timeout"]
        )
        response.raise_for_status()
        
        data = response.json()
        content = data['choices'][0]['message']['content']
        
        # Robust JSON extraction
        import re
        
        # 1. Remove <think>...</think> blocks (common in reasoning models)
        clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        
        # 2. Look for markdown code blocks ```json ... ``` or ``` ... ```
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', clean_content, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                result = json.loads(json_str)
                log_decision("ENGINE", "PROCESSING", "EXTRACT_JSON", "Success (Code Block)")
                result['original_input'] = user_text
                return result
            except:
                pass # Code block content wasn't valid, try fallback

        # 3. Fallback: Find the largest valid JSON object
        try:
            start_index = content.find('{')
            end_index = content.rfind('}')
            
            if start_index != -1 and end_index != -1:
                json_str = content[start_index : end_index + 1]
                result = json.loads(json_str)
                log_decision("ENGINE", "PROCESSING", "EXTRACT_JSON", "Success (Raw)")
                result['original_input'] = user_text
                return result
        except json.JSONDecodeError:
             # Try one more aggressive cleanup: remove everything that looks like a <tag>
             try:
                 cleaner = re.sub(r'<[^>]+>', '', content)
                 start = cleaner.find('{')
                 end = cleaner.rfind('}')
                 if start != -1 and end != -1:
                     json_str = cleaner[start : end + 1]
                     result = json.loads(json_str)
                     log_decision("ENGINE", "PROCESSING", "EXTRACT_JSON", "Success (Aggressive)")
                     result['original_input'] = user_text
                     return result
             except:
                 pass
            
        log_error("ENGINE", f"No JSON found in response: {content[:100]}...")
        
        # FALLBACK: Rule-based NLU
        lower_input = user_text.lower()
        if "prefer" in lower_input or "set" in lower_input and "format" in lower_input:
             log_decision("ENGINE", "FALLBACK", "RULE_MATCH", "Preference Update")
             return {
                 "intent": "preference_update",
                 "preference_data": user_text, # Just pass the whole text
                 "original_input": user_text
             }
        
        return {"error": "Failed to parse intent"}
        
    except requests.RequestException as e:
        log_error("ENGINE", f"LLM API Error: {e}")
        return {"error": "LLM API Unavailable"}
    except json.JSONDecodeError as e:
        log_error("ENGINE", f"JSON Parse Error: {e} | Content: {content}")
        return {"error": "Failed to parse intent"}

import datetime

# ... (Previous imports)

def generate_summary(data_block, user_query=""):
    """
    Pass 2: Converts raw data block into natural language.
    """
    from .prompts import SUMMARY_TRANSLATOR_PROMPT
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M %p")
    
    prompt = SUMMARY_TRANSLATOR_PROMPT.format(
        current_time=current_time,
        user_query=user_query,
        task_list=data_block
    )
    
    payload = {
        "model": ACTIVE_MODEL_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        **LM_STUDIO_SETTINGS
    }
    # Override temp for summary? 0.7 set in config logic?
    # No, config has 0.3. Summary needs creative.
    payload["temperature"] = 0.7
    
    try:
        response = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Remove any <think> blocks if they appear
        import re
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        
        log_decision("ENGINE", "GENERATION", "SUMMARIZE", "Success")
        return content.strip()
        
    except Exception as e:
        log_error("ENGINE", f"Summary Generation Error: {e}")
        return "I have the data, but I'm having trouble reading it out loud."

def generate_answer_from_notes(user_question):
    """
    RAG Answer Generation: Reads notes and answers the question.
    """
    context = ""
    now = datetime.datetime.now()
    # Pre-calculate common formats for the LLM to pick from or assemble
    time_components = {
        "time_12h": now.strftime("%I:%M %p"),
        "time_24h": now.strftime("%H:%M"),
        "day": now.strftime("%d"),
        "month": now.strftime("%m"),
        "year": now.strftime("%Y"),
        "weekday": now.strftime("%A"),
        "full_date": now.strftime("%Y-%m-%d")
    }
    
    # Load Profile
    profile = ""
    try:
        with open("data/profile.json", "r") as f:
            profile = f.read()
    except Exception:
        pass

    try:
        from modules import librarian
        librarian.ingest_file("data/notes/athena.txt")
        results = librarian.query_knowledge(user_question, n_results=3)
        context = "\n\n".join(results)
        
        if not context:
            pass 
            
    except Exception as e:
        log_error("ENGINE", f"Librarian Error: {e}")
        return "I'm having trouble accessing my memory."

    prompt = f"""
    You are Project Athena.
    
    Current Time Data:
    - Time (12h): {time_components['time_12h']}
    - Time (24h): {time_components['time_24h']}
    - Day: {time_components['day']}
    - Month: {time_components['month']}
    - Year: {time_components['year']}
    - Weekday: {time_components['weekday']}
    
    User Profile:
    {profile}
    
    Instructions:
    1. Answer the question based on the Context below.
    2. If asked for the time:
       - CHECK 'time_format_preference' OR 'new_time_format_request' in User Profile.
       - IF FOUND, use that format string EXACTLY.
         - You MUST replace ALL placeholders (e.g. DD, MM, YYYY) even if the user only asked for "Time".
         - Example: If format is "HH:MM DD-MM-YYYY", output "01:30 PM 12-02-2026".
       - IF NOT FOUND, use the standard format.
       - CONSTRUCT the string using the Data above.
       - Output ONLY the final formatted string.
    
    Context:
    {context}
    
    Question: {user_question}
    
    Answer:
    """
    
    payload = {
        "model": ACTIVE_MODEL_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        **LM_STUDIO_SETTINGS
    }
    payload["temperature"] = 0.7
    
    try:
        response = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        import re
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        
        log_decision("ENGINE", "GENERATION", "ANSWER_QUERY", "Success")
        return content.strip()
        
    except Exception as e:
        log_error("ENGINE", f"Answer Generation Error: {e}")
        return "I'm having trouble thinking of an answer right now."
