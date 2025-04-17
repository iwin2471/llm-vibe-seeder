from transformers import pipeline, set_seed
from src.generator.llm_loader import manager


def get_sampling_params(ocean: dict) -> dict:
    """
    Generate dynamic temperature and top_p based on OCEAN profile.
    """

    openness = ocean.get("openness", 0.5)
    conscientiousness = ocean.get("conscientiousness", 0.5)
    extraversion = ocean.get("extraversion", 0.5)
    agreeableness = ocean.get("agreeableness", 0.5)
    neuroticism = ocean.get("neuroticism", 0.5)

    top_p = min(1.0, 0.85 + openness * 0.15 + neuroticism * 0.1)
    temperature = 0.3 + (extraversion * 0.4) - (conscientiousness * 0.3)
    top_p = round(min(max(top_p, 0.6), 1.0), 2)
    temperature = round(min(max(temperature, 0.3), 1.2), 2)

    return {"temperature": temperature, "top_p": top_p}


def generate_character(ocean: dict) -> str:

    prompt = manager.generate_prompt("character_creation", openness=ocean['openness'],
        conscientiousness=ocean['conscientiousness'],
        extraversion=ocean['extraversion'],
        agreeableness=ocean['agreeableness'],
        neuroticism=ocean['neuroticism'])
    
    params = get_sampling_params(ocean)
    
    result = manager.call_webui_api(prompt, max_tokens=300, temperature=params["temperature"], top_p=params["top_p"])
    return result


