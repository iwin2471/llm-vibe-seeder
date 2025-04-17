from typing import Dict
from src.generator.character_generator import generate_character
import json
import os
import re
import random


def clean_output(raw_text: str) -> dict:
    """
    Parse LLM output to clean JSON-ready dict
    """

    parts = {
        "name": "",
        "traits": [],
        "style": "",
        "background": "",
        "vibe_keywords": [],
        "core_seed": 0
    }

    current_key = None

    for line in raw_text.splitlines():
        line = line.strip()

        if line.lower().startswith("name:"):
            current_key = "name"
            parts["name"] = line.split(":", 1)[1].strip()

        elif line.lower().startswith("traits:"):
            current_key = "traits"

        elif line.lower().startswith("speaking style:"):
            current_key = "style"
            parts["style"] = line.split(":", 1)[1].strip()

        elif line.lower().startswith("backstory:"):
            current_key = "background"
            parts["background"] = line.split(":", 1)[1].strip()

        elif line.lower().startswith("vibe keywords:"):
            current_key = "vibe_keywords"

        elif line.lower().startswith("core seed"):
            current_key = "core_seed"
            seed_part = re.findall(r'\d+', line)
            if seed_part:
                parts["core_seed"] = int(seed_part[0])

        else:
            if current_key == "traits":
                if line:
                    parts["traits"].append(line)
            elif current_key == "vibe_keywords":
                if line:
                    parts["vibe_keywords"].append(line)

    return parts

def generate_ocean_profile() -> Dict[str, float]:
        return {
            "openness": random.uniform(0, 1),
            "conscientiousness": random.uniform(0, 1),
            "extraversion": random.uniform(0, 1),
            "agreeableness": random.uniform(0, 1),
            "neuroticism": random.uniform(0, 1),
        }
        
        
def main():
    print("=== vibe-seeder AI Character Creator ===\n")

    ocean = generate_ocean_profile()
    print("=== OCEAN PROFILE ===")
    print(json.dumps(ocean, indent=2, ensure_ascii=False))

    print("\nGenerating Character from OCEAN...")
    raw_result = generate_character(ocean)

    print("\n=== RAW OUTPUT ===\n")
    print(raw_result)

    persona = clean_output(raw_result)

    print("\n=== CLEANED CHARACTER ===\n")
    print(json.dumps(persona, indent=2, ensure_ascii=False))

    filename = persona["name"].lower().replace(" ", "_")

    output_path = os.path.join("data/characters", f"{filename}.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(persona, f, indent=2, ensure_ascii=False)

    print(f"\nCharacter saved to {output_path}")



