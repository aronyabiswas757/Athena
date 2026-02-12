"""
Router Module: Dispatches intents to specific modules.
"""
import logging
from modules import scheduler, sanitizer
from core import monitor

logger = logging.getLogger("athena")

def route_intent(data):
    """
    Routes the NLU output to the correct action.
    """
    intent = data.get("intent")
    
    if intent == "schedule_add":
        task_name = data.get("task_name")
        relative_time = data.get("relative_time")
        
        if not task_name or not relative_time:
            return "Missing task details."
            
        # Sanitize time
        execution_time = sanitizer.parse_relative_time(relative_time)
        
        if not execution_time:
            return f"Could not understand the time: {relative_time}"
            
        # Persist
        success = scheduler.add_task(task_name, execution_time)
        
        if success:
            return f"Saved. I will remind you to '{task_name}' at {execution_time.strftime('%H:%M')}."
        else:
            return "Failed to save the task to database."
            
    elif intent == "query_schedule":
        # Pass 1: Fetch rigid data
        raw_data = scheduler.get_today_summary()
        
        # Pass 2: Translate via LLM (Reuse engine logic or direct request? 
        # Engine is currently setup for classification. We might need a helper or just call requests here.)
        # To keep it clean, let's add a 'generate_response' to engine.py or just do it here.
        # Let's import engine to use its config/setup but we have a circular dependency risk if engine imports router.
        # Router is imported by main. Engine is imported by main.
        # Router imports scheduler.
        # Let's add 'summarize' function to engine? No, engine imports prompts. 
        # Let's just do a quick request here using config settings, 
        # OR better: add `engine.generate_text(prompt)` and import it.
        # Wait, engine.py imports prompts.
        
        from core import engine 
        # Note: Circular import risk if engine imports router. 
        # Current: 
        # main -> core.engine
        # main -> core.router
        # core.router -> module...
        # core.engine -> ...
        # If router imports engine, and engine doesn't import router (it doesn't), we are fine.
        
        # We need a new function in engine for generation, not classification.
        user_input = data.get("original_input", "")
        response = engine.generate_summary(raw_data, user_query=user_input)
        return response
    
    elif intent == "state_change":
        new_state = data.get("new_state")
        if new_state:
            # Map friendly names if LLM messes up, though prompt says rigid enum.
            # Assuming LLM follows prompt:
            if monitor.set_state(new_state):
                return f"State changed to {new_state}."
            else:
                return f"Invalid state requested: {new_state}"
        else:
            return "No state specified."
            
    elif intent == "knowledge_query":
        from core import engine
        # We pass the original user input text (Wait, we need the input text)
        # The 'data' dict usually comes from engine.process_input which returns JSON.
        # It DOES NOT return the original user text.
        # We need to pass user_text to route_intent? 
        # Or store it in the data dict?
        # Let's update engine.process_input to include "original_input" in the returned dict.
        
        # Checking router.py signature: def route_intent(data):
        # We need to update engine.py first to inject the input.
        
        # Assuming we will fix engine.py, let's write the router logic assuming data['original_input'] exists.
        user_input = data.get("original_input", "")
        return engine.generate_answer_from_notes(user_input)

    elif intent == "preference_update":
        # Just acknowledge it. The learner will pick it up from logs.
        return "Got it. I've made a note of your preference."
        
    else:
        return f"Unknown intent: {intent}"