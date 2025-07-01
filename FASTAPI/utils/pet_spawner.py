from utils.species_loader import load_all_pet_species
from models.models import Pet
import random

async def spawn_random_pet(user_id: int, db):
    """
    Создаёт случайного питомца на основе всех species из pet_species.json.
    Поддерживает гибридов (race_mix), spawn_variants, trait_pool.
    """
    species_data = load_all_pet_species()
    weighted_species = []

    for code, data in species_data.items():

            # ⛔ защита от пустых species_code
            if not code or not isinstance(code, str) or code.strip() == "":
                print(f"[SKIP] invalid species_code: {repr(code)}")
                continue

            weight = data.get("spawn_rules", {}).get("weight", 1.0)
            weighted_species.append((code, data, weight))

    if not weighted_species:
        raise ValueError("❌ Нет подходящих питомцев для спауна")

    # выбор по весам
    choices  = [(code, data) for code, data, _ in weighted_species]
    weights  = [weight for _, _, weight in weighted_species]
    selected_code, selected = random.choices(choices, weights=weights)[0]

    # картинка
    image_variants = selected.get("spawn_variants") or [selected.get("image", "noimage.png")]
    image_name     = random.choice(image_variants)

    # черта
    trait_pool = selected.get("trait_pool") or selected.get("default_traits", ["silent"])
    trait_pick = random.choice(trait_pool)

    # вычисляем race_code (поддержка race_mix)
    race_code = selected.get("race_code")
    if not race_code:
        mix = selected.get("race_mix")
        if isinstance(mix, list) and mix:
            race_code = "+".join(mix)
        else:
            race_code = "unknown"

    return Pet(
        user_id      = user_id,
        species_code = selected_code,  # теперь гарантированно ≠ None
        race_code    = race_code,
        name         = "...",
        image        = f"pets/{image_name}",
        trait        = trait_pick,
)