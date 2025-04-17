from src.engine.core import VibeCharacter


def main():
    print("=== vibe-seeder: Luna Story ===\n")

    luna = VibeCharacter("luna")

    print(luna.introduce())

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Ending chat with Luna.")
            break

        response = luna.chat(user_input)
        print(f"\n{luna.name}: {response}")


if __name__ == "__main__":
    main()
