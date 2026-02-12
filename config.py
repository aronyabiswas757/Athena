"""
Configuration settings for Project Athena.
"""
import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "athena.db")
LOG_DIR = os.path.join(DATA_DIR, "logs")

MODELS_DIR = os.path.join(BASE_DIR, "models")
BIN_DIR = os.path.join(BASE_DIR, "bin")

# LM Studio Configuration
LM_STUDIO_URL = "http://localhost:1234/v1"

# Generation Settings
# Increase max_tokens to allow for "reasoning" (<think> blocks) followed by JSON
LM_STUDIO_SETTINGS = {
    "temperature": 0.3, # Slightly higher to avoid repetition loops in reasoning models
    "max_tokens": 4096, # Reverted to 4096 to avoid 400 Bad Request (Server Limit)
    "top_p": 0.95,      # Nucleus sampling
    "presence_penalty": 0.2, # Discourage repetition
    "timeout": 30
} 

# Model Identification
PREFERRED_MODELS = [
    "qwen2.5-3b-instruct",
    "mistralai/ministral-3-3b", 
    "qwen3-8b"
]
# Legacy support
PREFERRED_MODEL = PREFERRED_MODELS[0]

# System Settings
POLL_INTERVAL_SECONDS = 60
