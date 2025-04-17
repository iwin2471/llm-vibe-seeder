import json
import os
from datetime import datetime


def log_interaction(character_name: str, user_input: str, response: str, seed: int):
    """
    Log the interaction with mood, seed, and messages.
    """

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "character": character_name,
        "seed": seed,
        "user_input": user_input,
        "response": response
    }

    log_path = os.path.join("logs", "vibe_log.json")

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # Append to log
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
