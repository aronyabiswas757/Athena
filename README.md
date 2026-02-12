# Project Athena

**Project Athena** is a modular, offline-first AI assistant designed for productivity and privacy. It integrates Natural Language Understanding (NLU), Retrieval-Augmented Generation (RAG), and Voice Interaction into a lightweight Python application.

## Core Features
- **Offline Intelligence**: Powered by local LLMs via LM Studio (verified with `mistralai/ministral-3-3b` and `qwen2.5-3b-instruct`).
- **Real-Time Context**: Aware of the current system time and date.
- **Smart Scheduling**: Manages tasks and reminders with natural language (e.g., "Remind me to call John in 20 minutes").
- **Hybrid NLU**: Uses a robust mix of LLM intent classification and rule-based fallbacks.
- **Memory & Reflection**: "Learns" from daily interactions and updates a user profile automatically.
- **Voice Output**: Provides concise, natural language responses via TTS.

## Requirements
- Python 3.10+
- [LM Studio](https://lmstudio.ai/) (running a local server)

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/aronyabiswas757/athena.git
    cd athena
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure LM Studio**:
    - Load a model (e.g., `qwen2.5-3b-instruct`).
    - Start the Local Server on port `1234`.
    - Ensure `Context Handling` is set to keep system prompts.

## Usage

1.  **Start the Assistant**:
    ```bash
    python main.py
    ```

2.  **Interact**:
    - Type or speak (if STT enabled) your commands.
    - Examples:
        - "What time is it?"
        - "Remind me to check emails at 5 PM."
        - "Do I have any meetings today?"
        - "I prefer 12-hour time format."

## Configuration
Edit `config.py` to adjust settings:
- `PREFERRED_MODELS`: List of model IDs (priority order). Athena will use the first available one.
- `LM_STUDIO_URL`: defaults to `http://localhost:1234/v1`.

### User Profile
You can manually edit `data/profile.json` to set preferences, for example:
```json
{
  "learned_preferences": {
    "time_format_preference": "HH:MM AM/PM DD-MM-YYYY"
  }
}
```

## Structure
- `core/`: Main logic (Engine, Router, Learner).
- `modules/`: Capabilities (Scheduler, Voice, Librarian).
- `data/`: Storage (Databases, Logs, Profile).
- `test/`: Test suite.

## License
MIT License. See `LICENSE` for details.
