#!/usr/bin/env python3
import os
import argparse
import json
from colorama import init, Fore, Style
from src.tools.create_character import generate_ocean_profile, clean_output
from src.generator.character_generator import generate_character
from src.tools.character_card import create_character_card

def print_header(text):
    """Print a styled header"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}{text}{Style.RESET_ALL}")

def generate_complete_character():
    """Generate a character and its card in one process"""
    init()  # Initialize colorama for colored output
    
    print_header("=== vibe-seeder Procedural Character Creator v0.2 ===")
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate a character and character card")
    parser.add_argument("--output-dir", default="data/characters", help="Directory to save character files")
    args = parser.parse_args()
    
    # Generate random OCEAN profile
    print_header("Generating random character...")
    ocean = generate_ocean_profile()
    
    print_header("OCEAN Profile")
    print(json.dumps(ocean, indent=2, ensure_ascii=False))

    # Character generation
    print_header("Generating Character...")
    raw_result = generate_character(ocean)

    print("\nRaw LLM output:")
    print(raw_result)

    # Clean and parse character data
    persona = clean_output(raw_result)

    print_header("Character Profile")
    print(json.dumps(persona, indent=2, ensure_ascii=False))

    # Create data directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Save character data
    name_slug = persona["name"].lower().replace(" ", "_")
    character_path = os.path.join(args.output_dir, f"{name_slug}.json")
    
    with open(character_path, 'w', encoding='utf-8') as f:
        json.dump(persona, f, indent=2, ensure_ascii=False)
    
    print_success(f"Character saved to {character_path}")

    # Generate character card
    card_path = os.path.join(args.output_dir, f"{name_slug}_card.png")
    create_character_card(persona, card_path)
    
    print_success(f"Generated character card saved to {card_path}")
    
    return persona

if __name__ == "__main__":
    generate_complete_character() 