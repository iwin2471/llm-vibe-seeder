import json
from src.persona.persona_loader import load_persona
from src.seeder.seed_generator import generate_seed
from src.responder.responder import generate_response
from src.utils.logger import log_interaction


class VibeCharacter:
    def __init__(self, character_name: str):
        self.persona = load_persona(character_name)
        self.seed = self.persona.get("core_seed", None)
        self.name = self.persona["name"]

    def introduce(self):
        intro = f"Hi, I'm {self.name}."
        if not self.seed:
            intro += " I don't have a core seed yet!"
        else:
            intro += f" My core seed is {self.seed}."
        return intro

    def chat(self, user_input: str):
        # Generate new seed based on mood if dynamic
        self.seed = generate_seed(self.persona)

        # Generate response based on enforced seed
        response = generate_response(user_input, self.persona, self.seed)

        # Log it
        log_interaction(self.name, user_input, response, self.seed)

        return response
