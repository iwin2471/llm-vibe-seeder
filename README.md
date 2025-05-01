# vibe-seeder

*vibe-seeder* is an experimental project exploring LLM-based role-playing characters with self-driven mood & randomness control.

---

## Why this project?

While playing with [text-generation-webui](https://github.com/oobabooga/text-generation-webui), I realized that seed value controls much more than just randomness.

Seed directly impacts the *vibe* of a character's output.

So this project is my way to go deep into:
- Seed as personality driver
- Seed as mood evolution tool
- Seed as story mechanic

---

## Core Idea

> Characters pick their own vibe → generate their own seed → live with it.

---

## Main Goals of vibe-seeder

1. Characters describe their current mood/vibe
2. Characters generate their own seed (in dialogue)
3. That seed is actually used as LLM sampling seed (affecting next response)
4. Logs & tracks mood & seed history over time

---

## Current Status - v0.3

### Phase 2 Features (Complete):
- Procedural Character Creator
- Random OCEAN personality profiles
- Automatic seed generation for personality consistency
- Visual character cards
- Improved CLI with multiple options

### Phase 3 Features (New):
- Memory System - characters remember past conversations
- Automatic conversation summarization
- Retrieval-Augmented Generation (RAG)
- Contextual memory retrieval based on conversation
- Enhanced logging of interactions and memories
- Interactive chat interface with memory persistence

---

## Running the Project

### Installation

1. Clone the repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Make sure you have a local LLM running (via text-generation-webui or similar)

### Usage

```bash
# Create a complete character with visualization
python -m vibe-seeder complete

# Chat with a character (with memory)
python -m vibe-seeder chat

# Generate a card for an existing character
python -m vibe-seeder card data/characters/your_character.json

# Get help
python -m vibe-seeder help
```

### Character Creation

The character creator automatically generates a new character using:
- Random OCEAN personality profile (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
- Dynamic sampling parameters based on personality
- Automatic seed generation for consistent character vibes
- Visual character cards showing traits and personality

### Character Chat with Memory

The chat interface allows you to:
- Select and talk to your characters
- Characters automatically remember important parts of conversations
- Relevant memories are retrieved when contextually appropriate
- Each character's memories are stored separately
- All interactions are logged for analysis

---

## Future Ideas
- Phase 4: Mood drift engine (seed evolution)
- Phase 4: Emotion-state-driven seed fluctuation
- Phase 4: Auto-personality mutation over time
- Seed-based story arcs
- Multi-character interactions with shared memory

---

## Contributing

This is an experimental project. Feel free to fork, experiment, and pull request.

