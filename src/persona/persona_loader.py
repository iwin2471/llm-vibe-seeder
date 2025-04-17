import json
import os


def load_persona(character_name: str) -> dict:
    """
    Load character persona JSON file.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    persona_path = os.path.normpath(os.path.join(base_path, "..", "..", "data", "characters", f"{character_name.lower()}.json"))

    if not os.path.exists(persona_path):
        raise FileNotFoundError(f"Persona file not found for {character_name} at {persona_path}")

    with open(persona_path, 'r', encoding='utf-8') as f:
        persona = json.load(f)

    return persona
