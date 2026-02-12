"""
Voice Module: Handles Text-to-Speech synthesis using pyttsx3 (Native OS TTS).
"""
import pyttsx3
import logging
import threading

logger = logging.getLogger("athena")

# Initialize engine globally? 
# pyttsx3 can be finicky with threads. 
# It's often safer to initialize it in the thread that uses it, or use a queue.
# However, for a simple implementation, let's try a lock-protected shared function 
# or just re-initialize for each speak (can be slow) or keep a global instance.

# Best practice for pyttsx3 in a background thread:
# runAndWait() blocks.
# We will create a simple function that creates an engine, speaks, and closes.
# Or better, we just use it directly since monitor is a single thread.

def speak(text):
    """
    Converts text to speech using native OS capabilities.
    Blocking call.
    """
    try:
        # Initialize the engine
        engine = pyttsx3.init()
        
        # Optional: Configure voice (Speed, Volume)
        engine.setProperty('rate', 170)  # Speed percent (can go over 100)
        engine.setProperty('volume', 1.0)  # Volume 0-1

        # Queue the command
        engine.say(text)
        
        # Block until finished
        engine.runAndWait()
        
        # Stop the loop (important if we re-initialize)
        engine.stop()
        
        logger.info(f"Spoken: {text}")
        
    except Exception as e:
        logger.error(f"TTS Error: {e}")
