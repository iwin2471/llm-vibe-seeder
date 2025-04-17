from transformers import pipeline, set_seed
import torch


# Load your local model here
# Customize your model path if needed
generator = pipeline("text-generation", model="gpt2", device=0 if torch.cuda.is_available() else -1)


def generate_response(user_input: str, persona: dict, seed: int) -> str:
    """
    Generate a response from LLM with enforced sampling seed.
    """

    set_seed(seed)

    prompt = f"{persona['name']} is {', '.join(persona['traits'])}.\nUser: {user_input}\n{persona['name']}:"

    result = generator(prompt, max_length=100, num_return_sequences=1, do_sample=True)[0]['generated_text']

    # Clean output: return only LLM response
    response = result.split(f"{persona['name']}:")[-1].strip()

    return response
