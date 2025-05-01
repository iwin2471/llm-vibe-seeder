import os
import json
import argparse
from PIL import Image, ImageDraw, ImageFont
import colorsys
import hashlib
import random
from typing import Dict, Any, Tuple

def load_character(character_path: str) -> Dict[str, Any]:
    """Load character data from JSON file"""
    try:
        with open(character_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Character file '{character_path}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Character file '{character_path}' is not valid JSON.")
        exit(1)

def seed_to_color(seed: int) -> Tuple[int, int, int]:
    """Generate a color from a seed value"""
    # Use seed to create a hash
    hash_str = hashlib.md5(str(seed).encode()).hexdigest()
    
    # Use parts of the hash to influence the HSV color
    h = int(hash_str[0:2], 16) / 255.0  # Hue from first byte
    s = 0.7 + (int(hash_str[2:4], 16) / 255.0) * 0.3  # Saturation 0.7-1.0
    v = 0.6 + (int(hash_str[4:6], 16) / 255.0) * 0.4  # Value 0.6-1.0
    
    # Convert HSV to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def get_contrasting_text_color(bg_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Determine whether to use white or black text based on background color"""
    luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]) / 255
    return (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

def create_character_card(character: Dict[str, Any], output_path: str) -> None:
    """Generate a character card image from character data"""
    # Card dimensions
    width, height = 800, 1000
    
    # Generate a background color based on the character's seed
    bg_color = seed_to_color(character.get('core_seed', random.randint(10000, 99999999)))
    text_color = get_contrasting_text_color(bg_color)
    
    # Create a new image with the background color
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts, fall back to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        subtitle_font = ImageFont.truetype("arial.ttf", 40)
        regular_font = ImageFont.truetype("arial.ttf", 30)
        small_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        # Fall back to default font
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw name
    name = character.get('name', 'Unknown Character')
    draw.text((width // 2, 80), name, fill=text_color, font=title_font, anchor="mm")
    
    # Draw traits
    traits = character.get('traits', [])
    traits_y = 160
    draw.text((50, traits_y), "Traits:", fill=text_color, font=subtitle_font)
    traits_y += 60
    for trait in traits:
        draw.text((70, traits_y), f"• {trait}", fill=text_color, font=regular_font)
        traits_y += 40
    
    # Draw speaking style
    style_y = traits_y + 30
    draw.text((50, style_y), "Speaking Style:", fill=text_color, font=subtitle_font)
    style_y += 60
    style_text = character.get('style', 'No defined speaking style.')
    
    # Word wrap for style text
    words = style_text.split()
    lines = []
    line = []
    for word in words:
        if len(' '.join(line + [word])) <= 70:  # Adjust based on font and image width
            line.append(word)
        else:
            lines.append(' '.join(line))
            line = [word]
    if line:
        lines.append(' '.join(line))
    
    for line in lines:
        draw.text((70, style_y), line, fill=text_color, font=regular_font)
        style_y += 40
    
    # Draw vibe keywords
    keywords_y = style_y + 30
    draw.text((50, keywords_y), "Vibe Keywords:", fill=text_color, font=subtitle_font)
    keywords_y += 60
    keywords = character.get('vibe_keywords', [])
    keyword_text = ', '.join(keywords)
    
    # Word wrap for keywords
    words = keyword_text.split()
    lines = []
    line = []
    for word in words:
        if len(' '.join(line + [word])) <= 70:
            line.append(word)
        else:
            lines.append(' '.join(line))
            line = [word]
    if line:
        lines.append(' '.join(line))
    
    for line in lines:
        draw.text((70, keywords_y), line, fill=text_color, font=regular_font)
        keywords_y += 40
    
    # Draw seed at bottom
    seed = character.get('core_seed', 'N/A')
    draw.text((width // 2, height - 50), f"Seed: {seed}", fill=text_color, font=small_font, anchor="mm")
    
    # Save the image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Character card saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate character cards from character JSON files")
    parser.add_argument("character_file", help="Path to character JSON file")
    parser.add_argument("--output", "-o", help="Output path for character card image (default: same directory as JSON)")
    args = parser.parse_args()
    
    # Load character data
    character = load_character(args.character_file)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        base_name = os.path.splitext(args.character_file)[0]
        output_path = f"{base_name}_card.png"
    
    # Create character card
    create_character_card(character, output_path)

if __name__ == "__main__":
    main() 