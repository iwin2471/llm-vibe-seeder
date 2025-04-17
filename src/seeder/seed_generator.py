import random


def generate_seed(persona: dict) -> int:
    """
    Generate a seed based on persona's OCEAN profile.
    """

    ocean = persona.get("ocean", {})
    base = 10000000

    # Openness: add variance
    openness = ocean.get("openness", 0.5)
    base += int(openness * random.randint(100000, 999999))

    # Conscientiousness: lowers base (more tidy)
    conscientiousness = ocean.get("conscientiousness", 0.5)
    base -= int(conscientiousness * random.randint(100000, 500000))

    # Extraversion: repeats digits more likely
    extraversion = ocean.get("extraversion", 0.5)
    if extraversion > 0.7:
        repeated = str(random.choice(range(1, 10))) * 4
        base = int(repeated + str(base)[-4:])

    # Agreeableness: lower → more chaos
    agreeableness = ocean.get("agreeableness", 0.5)
    if agreeableness < 0.3:
        base += random.randint(100000, 999999)

    # Neuroticism: oddify seed
    neuroticism = ocean.get("neuroticism", 0.5)
    if neuroticism > 0.6:
        if base % 2 == 0:
            base += 1

    return abs(base)
