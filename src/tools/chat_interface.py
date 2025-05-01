#!/usr/bin/env python
import os
import sys
import json
import argparse
import readline  # For better input handling
from colorama import init, Fore, Style, Back
from typing import Optional, Dict

from src.responder.responder import generate_response, load_character, ChatSession
from src.utils.logger import log_interaction


def print_header(text: str, color=Fore.CYAN):
    """Print a styled header"""
    print(f"\n{color}{Style.BRIGHT}{text}{Style.RESET_ALL}")


def print_character_message(character_name: str, message: str):
    """Print a character's message with styling"""
    print(f"{Fore.GREEN}{Style.BRIGHT}{character_name}{Style.RESET_ALL}: {message}")


def print_user_message(message: str):
    """Print the user's message with styling"""
    print(f"{Fore.BLUE}{Style.BRIGHT}You{Style.RESET_ALL}: {message}")


def print_system_message(message: str):
    """Print a system message with styling"""
    print(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")


def list_available_characters():
    """List available characters in the data directory"""
    characters_dir = os.path.join("data", "characters")
    
    if not os.path.exists(characters_dir):
        print_system_message("No characters found. Create a character first.")
        return []
    
    character_files = [f for f in os.listdir(characters_dir) if f.endswith('.json')]
    
    if not character_files:
        print_system_message("No characters found. Create a character first.")
        return []
    
    print_header("Available Characters:")
    
    characters = []
    for i, char_file in enumerate(character_files, 1):
        char_path = os.path.join(characters_dir, char_file)
        try:
            with open(char_path, 'r', encoding='utf-8') as f:
                char_data = json.load(f)
                char_name = char_data.get('name', 'Unknown')
                characters.append((char_name, char_path))
                print(f"{i}. {char_name}")
        except json.JSONDecodeError:
            continue
    
    return characters


def select_character():
    """Prompt user to select a character"""
    characters = list_available_characters()
    
    if not characters:
        return None
    
    while True:
        choice = input("\nSelect a character (number or name), or press Enter to exit: ").strip()
        
        if not choice:
            return None
        
        # Try by number
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(characters):
                return characters[idx][1]  # Return path
        except ValueError:
            # Try by name
            for name, path in characters:
                if choice.lower() in name.lower():
                    return path
        
        print_system_message("Invalid selection. Please try again.")


def show_character_info(character: Dict):
    """Display character information"""
    print_header(f"Character Profile: {character.get('name', 'Unknown')}")
    
    if 'traits' in character and character['traits']:
        print(f"{Fore.YELLOW}Traits:{Style.RESET_ALL} {', '.join(character['traits'])}")
    
    if 'style' in character and character['style']:
        print(f"{Fore.YELLOW}Speaking Style:{Style.RESET_ALL} {character['style']}")
    
    if 'background' in character and character['background']:
        print(f"{Fore.YELLOW}Background:{Style.RESET_ALL} {character['background']}")
    
    print(f"{Fore.YELLOW}Core Seed:{Style.RESET_ALL} {character.get('core_seed', 'Unknown')}")
    print()  # Empty line for spacing


def run_chat_session(character_path: str):
    """Run an interactive chat session with a character"""
    character = load_character(character_path)
    
    if not character:
        print_system_message(f"Failed to load character from {character_path}")
        return
    
    # Initialize chat session
    chat_session = ChatSession(character)
    
    # Show character information
    show_character_info(character)
    
    print_header(f"Chat with {character['name']}")
    print_system_message("Type 'exit', 'quit', or press Ctrl+C to end the conversation.")
    
    try:
        while True:
            # Get user input
            user_input = input(f"{Fore.BLUE}{Style.BRIGHT}You:{Style.RESET_ALL} ").strip()
            
            if user_input.lower() in ('exit', 'quit', 'bye'):
                print_system_message(f"Ending conversation with {character['name']}...")
                break
                
            # Generate response with memory and RAG
            response, seed = generate_response(user_input, character, chat_session)
            
            # Display response
            print_character_message(character['name'], response)
            
            # Get memories that were used for logging
            memories_used = chat_session.memory_manager.retrieve_relevant_memories(
                user_input,
                chat_session.get_formatted_history(3),
                character.get('traits', [])
            )
            
            # Log the interaction
            log_interaction(
                character_name=character['name'],
                user_input=user_input,
                response=response,
                seed=seed,
                memories_used=memories_used
            )
            
    except KeyboardInterrupt:
        print("\n")
        print_system_message(f"Conversation with {character['name']} ended.")


def main():
    """Main CLI function"""
    init()  # Initialize colorama
    
    parser = argparse.ArgumentParser(description="Chat with AI characters using memory/RAG")
    parser.add_argument("--character", "-c", help="Path to character JSON file")
    args = parser.parse_args()
    
    # Either use provided character path or prompt user to select
    character_path = args.character
    if not character_path:
        character_path = select_character()
    
    if not character_path:
        print_system_message("No character selected. Exiting...")
        sys.exit(0)
    
    run_chat_session(character_path)


if __name__ == "__main__":
    main() 