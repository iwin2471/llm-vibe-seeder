import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.generator.llm_loader import manager


class MemoryManager:
    """
    Manages character memories, including creation, retrieval, and summarization.
    """
    
    def __init__(self, character_name: str):
        self.character_name = character_name
        self.memory_dir = os.path.join("data", "memories")
        self.memory_file = os.path.join(self.memory_dir, f"{character_name.lower().replace(' ', '_')}_memories.json")
        os.makedirs(self.memory_dir, exist_ok=True)
        self.memories = self._load_memories()
        
    def _load_memories(self) -> List[Dict[str, Any]]:
        """Load memories from file or create empty memory list"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading memory file for {self.character_name}. Creating new memories.")
                return []
        return []
    
    def _save_memories(self) -> None:
        """Save memories to file"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=2, ensure_ascii=False)
    
    def add_memory(self, content: str, importance: float = 0.5, 
                  metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a new memory
        
        Args:
            content: The text content of the memory
            importance: Memory importance rating (0.0-1.0)
            metadata: Optional additional data about the memory
        """
        if metadata is None:
            metadata = {}
            
        memory = {
            "id": len(self.memories) + 1,
            "timestamp": datetime.now().isoformat(),
            "unix_time": time.time(),
            "content": content,
            "importance": importance,
            "metadata": metadata
        }
        
        self.memories.append(memory)
        self._save_memories()
        
    def summarize_conversation(self, conversation_history: str) -> str:
        """
        Use LLM to summarize a conversation into a memory
        
        Args:
            conversation_history: The full conversation text
            
        Returns:
            A concise memory summary of the conversation
        """
        prompt = manager.generate_prompt("memory_summarization", 
                                       character_name=self.character_name,
                                       conversation_history=conversation_history)
        
        summary = manager.call_webui_api(prompt, max_tokens=100, temperature=0.7)
        return summary
    
    def retrieve_relevant_memories(self, user_input: str, current_conversation: str, 
                                 character_traits: List[str]) -> List[str]:
        """
        Retrieve memories relevant to current conversation context
        
        Args:
            user_input: The most recent user message
            current_conversation: The current conversation history
            character_traits: List of the character's traits
            
        Returns:
            List of relevant memory contents
        """
        if not self.memories:
            return []
            
        # If we have too few memories, just return all of them
        if len(self.memories) <= 3:
            return [memory["content"] for memory in self.memories]
        
        # Format all memories for retrieval prompt
        all_memories_text = "\n".join([
            f"Memory {i+1} ({memory.get('timestamp', 'unknown date')}): {memory['content']}"
            for i, memory in enumerate(self.memories)
        ])
        
        # Request memory retrieval via LLM
        prompt = manager.generate_prompt("memory_retrieval",
                                      character_name=self.character_name,
                                      traits=", ".join(character_traits),
                                      current_conversation=current_conversation,
                                      user_input=user_input,
                                      all_memories=all_memories_text)
        
        relevant_memories = manager.call_webui_api(prompt, max_tokens=200, temperature=0.7)
        
        # Return the raw relevant memories text
        return [relevant_memories]
    
    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Get all memories"""
        return self.memories
    
    def get_memory_by_id(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Get memory by ID"""
        for memory in self.memories:
            if memory["id"] == memory_id:
                return memory
        return None 