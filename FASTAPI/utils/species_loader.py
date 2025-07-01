import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET_SPECIES_PATH = os.path.join(BASE_DIR, "data", "pet_species.json")

def load_all_pet_species() -> dict:
    """
    Загружает pet_species.json и превращает список вида:
    [{ "mossback": {...} }, { "bonektra_wolf": {...} }] → в dict:
    { "mossback": {...}, "bonektra_wolf": {...} }
    """
    try:
        with open(PET_SPECIES_PATH, encoding="utf-8") as f:
            raw = json.load(f)

            if isinstance(raw, list):
                merged = {}
                for entry in raw:
                    if isinstance(entry, dict):
                        merged.update(entry)
                return merged

            elif isinstance(raw, dict):
                return raw  # на будущее: если решишь сделать JSON как flat-словарь

            else:
                raise ValueError("pet_species.json должен быть списком или словарём")

    except Exception as e:
        print(f"💥 Ошибка при загрузке pet_species.json: {e}")
        return {}


