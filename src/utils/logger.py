import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


def log_interaction(
    character_name: str, 
    user_input: str, 
    response: str, 
    seed: int, 
    memories_used: Optional[List[str]] = None,
    memory_added: Optional[str] = None
):
    """
    Log the interaction with mood, seed, and memories.
    
    Args:
        character_name: The character's name
        user_input: User's message
        response: Character's response
        seed: Seed used for generation
        memories_used: List of memories used for context (optional)
        memory_added: New memory created from this interaction (optional)
    """
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "character": character_name,
        "seed": seed,
        "user_input": user_input,
        "response": response,
        "memory": {
            "used": memories_used or [],
            "added": memory_added
        }
    }

    # Create character-specific log directory
    log_dir = os.path.join("logs", character_name.lower().replace(" ", "_"))
    log_path = os.path.join(log_dir, "interaction_log.json")
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Append to log
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            # If file is corrupted, start fresh
            logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
        
    # Also save to master log
    master_log_path = os.path.join("logs", "vibe_log.json")
    
    if os.path.exists(master_log_path):
        try:
            with open(master_log_path, "r", encoding="utf-8") as f:
                master_logs = json.load(f)
        except json.JSONDecodeError:
            master_logs = []
    else:
        master_logs = []
        
    master_logs.append(log_entry)
    
    with open(master_log_path, "w", encoding="utf-8") as f:
        json.dump(master_logs, f, ensure_ascii=False, indent=2)


def log_memory_creation(character_name: str, memory_content: str, importance: float, seed: int):
    """
    Log when a new memory is created
    
    Args:
        character_name: Character's name
        memory_content: Content of the memory
        importance: Importance score (0-1)
        seed: Seed associated with memory creation
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "character": character_name,
        "event_type": "memory_creation",
        "memory_content": memory_content,
        "importance": importance,
        "seed": seed
    }
    
    memory_log_path = os.path.join("logs", "memory_log.json")
    os.makedirs(os.path.dirname(memory_log_path), exist_ok=True)
    
    if os.path.exists(memory_log_path):
        try:
            with open(memory_log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []
        
    logs.append(log_entry)
    
    with open(memory_log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
