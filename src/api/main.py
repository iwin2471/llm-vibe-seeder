from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
import random
from pathlib import Path
from typing import Dict, List, Optional
import base64
from io import BytesIO

from src.tools.create_character import clean_output
from src.generator.character_generator import generate_character
from src.tools.character_card import create_character_card

# Create FastAPI app
app = FastAPI(
    title="Vibe-Seeder Character Creator",
    description="Web interface for creating characters with OCEAN traits",
    version="0.3"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create templates directory and templates object
templates_path = Path("src/api/templates")
templates_path.mkdir(parents=True, exist_ok=True)

# Create static files directory
static_path = Path("src/api/static")
static_path.mkdir(parents=True, exist_ok=True)

# Setup templates and static files
templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Make sure character data directory exists
characters_dir = Path("data/characters")
characters_dir.mkdir(parents=True, exist_ok=True)


def generate_ocean_profile() -> Dict[str, float]:
    """Generate random OCEAN personality profile"""
    return {
        "openness": random.uniform(0, 1),
        "conscientiousness": random.uniform(0, 1),
        "extraversion": random.uniform(0, 1),
        "agreeableness": random.uniform(0, 1),
        "neuroticism": random.uniform(0, 1),
    }


def save_character(character):
    """Save character to file"""
    filename = character["name"].lower().replace(" ", "_")
    output_path = characters_dir / f"{filename}.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(character, f, indent=2, ensure_ascii=False)
    
    return output_path


def create_character_image(character):
    """Create character card image and return path"""
    filename = character["name"].lower().replace(" ", "_")
    output_path = characters_dir / f"{filename}_card.png"
    
    create_character_card(character, str(output_path))
    
    return output_path


def image_to_base64(image_path):
    """Convert image to base64 for embedding in HTML"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with character creation form"""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request}
    )


@app.post("/api/characters", response_class=HTMLResponse)
async def create_character(
    request: Request,
    creation_method: str = Form(...),
    openness: Optional[float] = Form(None),
    conscientiousness: Optional[float] = Form(None),
    extraversion: Optional[float] = Form(None),
    agreeableness: Optional[float] = Form(None),
    neuroticism: Optional[float] = Form(None)
):
    """Create a character based on OCEAN traits"""
    # Determine if using random or custom OCEAN values
    if creation_method == "random":
        ocean = generate_ocean_profile()
    else:
        # Validate input values
        if None in [openness, conscientiousness, extraversion, agreeableness, neuroticism]:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "All OCEAN values must be provided"}
            )
        
        ocean = {
            "openness": max(0, min(1, openness)),
            "conscientiousness": max(0, min(1, conscientiousness)),
            "extraversion": max(0, min(1, extraversion)),
            "agreeableness": max(0, min(1, agreeableness)),
            "neuroticism": max(0, min(1, neuroticism)),
        }
    
    # Generate character
    raw_result = generate_character(ocean)
    
    # Parse output
    character = clean_output(raw_result)
    
    # Save character
    character_path = save_character(character)
    
    # Create character card
    card_path = create_character_image(character)
    
    # Convert image to base64 for display
    card_base64 = image_to_base64(card_path)
    
    return templates.TemplateResponse(
        "character_result.html",
        {
            "request": request,
            "character": character,
            "ocean": ocean,
            "card_base64": card_base64,
            "download_url": f"/api/characters/{character['name'].lower().replace(' ', '_')}/download"
        }
    )


@app.get("/api/characters/{character_name}/download")
async def download_character(character_name: str):
    """Download character JSON file"""
    file_path = characters_dir / f"{character_name}.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Character not found")
    
    return FileResponse(
        path=file_path,
        filename=f"{character_name}.json",
        media_type="application/json"
    )


@app.get("/api/characters/{character_name}/image/download")
async def download_character_image(character_name: str):
    """Download character card image"""
    file_path = characters_dir / f"{character_name}_card.png"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Character image not found")
    
    return FileResponse(
        path=file_path,
        filename=f"{character_name}_card.png",
        media_type="image/png"
    )


@app.get("/api/characters", response_class=JSONResponse)
async def list_characters_api():
    """API endpoint to list all characters"""
    characters = []
    
    for file in characters_dir.glob("*.json"):
        if file.is_file():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    character = json.load(f)
                    characters.append({
                        "name": character.get("name", "Unknown"),
                        "traits": character.get("traits", []),
                        "file": file.name,
                        "file_stem": file.stem,
                        "has_image": (characters_dir / f"{file.stem}_card.png").exists(),
                        "links": {
                            "self": f"/api/characters/{file.stem}",
                            "download": f"/api/characters/{file.stem}/download",
                            "image": f"/api/characters/{file.stem}/image"
                        }
                    })
            except json.JSONDecodeError:
                continue
    
    return {"characters": characters}


@app.get("/characters", response_class=HTMLResponse)
async def characters_page(request: Request):
    """Web page to list all characters"""
    characters = []
    
    for file in characters_dir.glob("*.json"):
        if file.is_file():
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    character = json.load(f)
                    characters.append({
                        "name": character.get("name", "Unknown"),
                        "traits": character.get("traits", []),
                        "style": character.get("style", ""),
                        "core_seed": character.get("core_seed", ""),
                        "file": file.name,
                        "file_stem": file.stem,
                        "has_image": (characters_dir / f"{file.stem}_card.png").exists()
                    })
            except json.JSONDecodeError:
                continue
    
    return templates.TemplateResponse(
        "characters_list.html", 
        {"request": request, "characters": characters}
    )


@app.get("/api/characters/{character_name}/image")
async def get_character_image(character_name: str):
    """Get character image for display in gallery"""
    file_path = characters_dir / f"{character_name}_card.png"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Character image not found")
    
    return FileResponse(
        path=file_path,
        media_type="image/png"
    )


@app.get("/api/characters/{character_name}", response_class=JSONResponse)
async def get_character(character_name: str):
    """Get a specific character's data as JSON"""
    file_path = characters_dir / f"{character_name}.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Character not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            character = json.load(f)
        
        # Add additional info about available resources
        character["links"] = {
            "self": f"/api/characters/{character_name}",
            "download": f"/api/characters/{character_name}/download",
            "image": f"/api/characters/{character_name}/image",
            "html_view": f"/characters/{character_name}"
        }
        
        return character
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading character: {str(e)}")


@app.get("/characters/{character_name}", response_class=HTMLResponse)
async def view_character(request: Request, character_name: str):
    """View a specific character's details"""
    file_path = characters_dir / f"{character_name}.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Character not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            character = json.load(f) 
        
        # Check if character image exists
        card_path = characters_dir / f"{character_name}_card.png"
        card_base64 = ""
        has_image = card_path.exists()
        if has_image:
            card_base64 = image_to_base64(card_path)
        
        # Get OCEAN profile from character data
        ocean_data = character.get("ocean", {})
        ocean = {
            "Openness": int(ocean_data.get("openness", 0.5) * 100),
            "Conscientiousness": int(ocean_data.get("conscientiousness", 0.5) * 100),
            "Extraversion": int(ocean_data.get("extraversion", 0.5) * 100),
            "Agreeableness": int(ocean_data.get("agreeableness", 0.5) * 100),
            "Neuroticism": int(ocean_data.get("neuroticism", 0.5) * 100)
        }
        
        return templates.TemplateResponse(
            "view_character.html",
            {
                "request": request,
                "character": character,
                "ocean": ocean,
                "card_base64": card_base64,
                "has_image": has_image,
                "file_stem": character_name,
                "download_url": f"/api/characters/{character_name}/download"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading character: {str(e)}")


def start():
    """Start the FastAPI app with uvicorn"""
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    start() 