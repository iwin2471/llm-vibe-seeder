#!/usr/bin/env python3
import uvicorn
import os
import sys

# Add parent directory to sys.path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

if __name__ == "__main__":
    print("Starting Vibe-Seeder Web Interface...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True) 