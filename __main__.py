import argparse
import sys
from src.tools.create_character import main as create_character
from src.tools.generate_complete_character import generate_complete_character
from src.tools.character_card import main as create_card
from src.tools.chat_interface import main as chat_interface

def show_help():
    print("vibe-seeder - LLM-based role-playing characters with mood & randomness control")
    print("\nCommands:")
    print("  character   - Create a new character with OCEAN traits")
    print("  complete    - Create a complete character with card (recommended)")
    print("  card        - Generate a card for an existing character")
    print("  chat        - Chat with a character (with memory/RAG)")
    print("  web         - Start web interface for character creation")
    print("  help        - Show this help message")
    print("\nExample usage:")
    print("  python -m vibe-seeder complete")
    print("  python -m vibe-seeder chat")
    print("  python -m vibe-seeder web")
    print("  python -m vibe-seeder card data/characters/emma_frost.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="vibe-seeder CLI", add_help=False)
    parser.add_argument('command', nargs='?', default='help', help='Command to run')
    parser.add_argument('args', nargs='*', help='Additional arguments')
    
    args = parser.parse_args()
    
    if args.command == 'character':
        sys.argv = [sys.argv[0]] + args.args
        create_character()
    elif args.command == 'complete':
        sys.argv = [sys.argv[0]] + args.args
        generate_complete_character()
    elif args.command == 'card':
        if not args.args:
            print("Error: Please provide a character file path")
            print("Example: python -m vibe-seeder card data/characters/character_name.json")
            sys.exit(1)
        sys.argv = [sys.argv[0]] + args.args
        create_card()
    elif args.command == 'chat':
        sys.argv = [sys.argv[0]] + args.args
        chat_interface()
    elif args.command == 'web':
        # Import here to avoid circular imports
        from src.api.main import start as start_web
        start_web()
    elif args.command == 'help' or args.command == '--help':
        show_help()
    else:
        print(f"Unknown command: {args.command}")
        show_help()
        sys.exit(1)
    
    