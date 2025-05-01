from typing import Dict, List, Optional, Tuple
import json
import os
from src.generator.llm_loader import manager
from src.memory.memory_manager import MemoryManager


class ChatSession:
    """
    Maintains the state of a conversation with memory and seed tracking
    """
    
    def __init__(self, character: Dict):
        self.character = character
        self.conversation_history = []
        self.memory_manager = MemoryManager(character['name'])
        self.current_seed = character.get('core_seed', 12345)
        
    def add_message(self, speaker: str, message: str) -> None:
        """Add a message to the conversation history"""
        self.conversation_history.append({
            "speaker": speaker,
            "message": message
        })
        
    def get_formatted_history(self, max_messages: int = 10) -> str:
        """Get formatted conversation history for prompt context"""
        # Get the last N messages
        recent_messages = self.conversation_history[-max_messages:] if max_messages > 0 else self.conversation_history
        
        formatted = ""
        for msg in recent_messages:
            if msg["speaker"] == "User":
                formatted += f"User: {msg['message']}\n"
            else:
                formatted += f"{self.character['name']}: {msg['message']}\n"
                
        return formatted
    
    def update_memory(self) -> None:
        """Update memory with a summary of the recent conversation"""
        if len(self.conversation_history) < 2:
            return  # Not enough conversation to summarize
            
        # Format last 10 messages for summarization
        conversation_text = self.get_formatted_history(10)
        
        # Get memory summary
        memory_summary = self.memory_manager.summarize_conversation(conversation_text)
        
        # Calculate importance based on conversation length and seed
        importance = min(0.9, 0.3 + (len(self.conversation_history) * 0.05))
        
        # Add to memory
        self.memory_manager.add_memory(
            content=memory_summary,
            importance=importance,
            metadata={"seed": self.current_seed}
        )


def generate_response(
    user_input: str, 
    persona: Dict, 
    chat_session: Optional[ChatSession] = None,
    seed: Optional[int] = None
) -> Tuple[str, int]:
    """
    Generate a response from LLM with memory and dynamic seeding.
    
    Args:
        user_input: The user's message
        persona: Character persona data
        chat_session: Optional chat session object (will create if None)
        seed: Optional seed to force (uses character seed or dynamic if None)
        
    Returns:
        Tuple of (response text, seed used)
    """
    # Initialize or use existing chat session
    if chat_session is None:
        chat_session = ChatSession(persona)
    
    # Set the seed value
    if seed is None:
        seed = persona.get('core_seed', 12345)
    
    # Add user message to history
    chat_session.add_message("User", user_input)
    
    # Format character traits
    traits_text = ", ".join(persona.get('traits', []))
    
    # Get relevant memories
    memories = chat_session.memory_manager.retrieve_relevant_memories(
        user_input, 
        chat_session.get_formatted_history(), 
        persona.get('traits', [])
    )
    
    # Format memories for prompt
    memory_text = "\n".join(memories) if memories else "No relevant memories."
    
    # Generate response with memories and conversation context
    prompt = manager.generate_prompt(
        "character_response",
        character_name=persona['name'],
        traits=traits_text,
        style=persona.get('style', ''),
        background=persona.get('background', ''),
        memory=memory_text,
        conversation_history=chat_session.get_formatted_history(),
        user_input=user_input
    )
    
    # Call the LLM with the character's seed
    response = manager.call_webui_api(
        prompt,
        max_tokens=150,
        temperature=0.8,
        top_p=0.9,
        seed=seed
    )
    
    # Add response to chat history
    chat_session.add_message(persona['name'], response)
    
    # Update memory with conversation summary
    chat_session.update_memory()
    
    return response, seed


def load_character(character_path: str) -> Dict:
    """Load a character from a JSON file"""
    try:
        with open(character_path, 'r', encoding='utf-8') as f:
            character = json.load(f)
        return character
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading character: {e}")
        return {}
