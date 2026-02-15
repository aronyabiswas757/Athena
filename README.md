# Project Athena

**Project Athena** is a modular, offline-first AI assistant designed for productivity and privacy. It integrates Natural Language Understanding (NLU), Retrieval-Augmented Generation (RAG), and Voice Interaction into a lightweight Python application.

## Core Features
- **Offline Intelligence**: Powered by local LLMs via LM Studio (verified with `ministral`,  `qwen2.5`).
- **Real-Time Context**: Aware of the current system time and date.
- **Smart Scheduling**: Manages tasks and reminders with natural language (e.g., "Remind me to call John in 20 minutes").
- **Hybrid NLU**: Uses a robust mix of LLM intent classification and rule-based fallbacks.
- **Memory & Reflection**: "Learns" from daily interactions and auto-updates the user profile.
- **Smart Model Selection**:
    - **Lazy Switching**: Respects your manually loaded model if it matches your preferences.
    - **Auto-Load**: Attempts to load your preferred model on startup if none are active.
    - **Auto-Load**: Attempts to load your preferred model on startup if none are active.
    - **Active Probe**: If no model is loaded, Athena actively probes the list of preferred models to find one that works.
- **Privacy First**: All data (Vector Store, SQL DB, Logs) is local and ignored by Git.

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
    - Load a model (e.g., `mistralai/ministral-3-3b`).
    - Start the Local Server on port `1234`.
    - Ensure `Context Handling` is set to keep system prompts.

## Usage

1.  **Start the Assistant**:
    ```bash
    python main.py
    ```
    *Note: On first run, Athena will automatically create a default `data/profile.json` user profile.*

2.  **Interact**:
    - Type or speak (if STT enabled) your commands.
    - Examples:
        - "What time is it?"
        - "Remind me to check emails at 5 PM."
        - "Do I have any meetings today?"
        - "I prefer 12-hour time format."

## Configuration
Edit `config.py` to adjust settings:
- `PREFERRED_MODELS`: List of model IDs (priority order). Athena uses "Lazy Switching" to respect your loaded model if it matches any tag in this list.
- `LM_STUDIO_URL`: defaults to `http://localhost:1234/v1`.

### User Profile
Athena manages `data/profile.json` automatically, but you can manually edit `learned_preferences` if needed:
```json
{
  "learned_preferences": {
    "time_format_preference": "HH:MM AM/PM DD-MM-YYYY"
  }
}
```

## Project Structure
- `core/`: Main logic (Engine, Router, Learner).
- `modules/`: Capabilities (Scheduler, Voice, Librarian).
- `data/`: Local Storage (Ignored by Git).
    - `knowledge_db/`: SQLite Database (`athena.db`).
    - `vector_store/`: FAISS Index (`vectors.index`).
    - `logs/`: Interaction and Decision logs.
    - `notes/`: Raw text files for RAG.
    - `profile.json`: User personality and preferences.
- `test/`: Test suite.

## License
MIT License. See `LICENSE` for details.
