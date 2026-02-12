"""
Project Athena: Main Entry Point
"""
import logging
import sys
import os

# Ensure we can import core/modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import LOG_DIR
from core import engine, router, monitor, learner
from modules import scheduler, voice
from core.logger import log_decision, log_interaction

# Logging is setup in core.logger


def main():
    print("Initializing Athena...")
    
    # Initialize DB
    scheduler.init_db()

    # Validate Brain
    print("Checking connection to Brain...")
    is_valid, model_id = engine.validate_model_connection()
    if not is_valid:
        print("ERROR: Athena Offline. Could not connect to LM Studio or no models loaded.")
        print("Please ensure LM Studio is running and a model is loaded.")
        sys.exit(1)
    
    print(f"Connected to Brain: {model_id}")
    
    # Start the Heart (Monitor)
    heart = monitor.Monitor()
    heart.start()
    
    print("Athena is online. Type 'exit' to quit.")
    print("Try: 'Remind me to call John in 20 minutes'")
    
    try:
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                break
                
            if not user_input:
                continue
                
            # Phase 1: Ingestion & Intent
            print("Thinking...")
            nlu_data = engine.process_input(user_input)
            
            if "error" in nlu_data:
                print(f"Athena: Error - {nlu_data['error']}")
                continue
                
            log_decision("MAIN", "INPUT_LOOP", "INTENT_DETECTED", str(nlu_data))
            
            # Phase 2 & 3: Sanitization & Persistence
            response = router.route_intent(nlu_data)
            
            # Output: Console + Voice (Clean)
            print(f"Athena: {response}")
            voice.speak(response)
            
            # Log interaction (includes timestamp in file, but not spoken)
            log_interaction(user_input, response)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        print("Reflecting on today's interactions...")
        learner.reflect()
        
        heart.stop()
        heart.join()
        print("Athena Offline.")

if __name__ == "__main__":
    main()
