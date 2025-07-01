import json
from collections import Counter
from pathlib import Path

PATH = Path("pet_species.json")

def load_species():
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)

def check_species(data):
    seen_codes = []
    errors = []

    for i, entry in enumerate(data):
        for code, spec in entry.items():
            location = f"[entry {i}]"

            # 1. code должен быть непустой строкой
            if not code or not isinstance(code, str) or code.strip() == "":
                errors.append(f"{location} ⛔ Пустой species_code: {repr(code)}")
                continue

            seen_codes.append(code)

            # 2. race_code или race_mix должен быть
            if not spec.get("race_code") and not spec.get("race_mix"):
                errors.append(f"{location} {code} — нет race_code и race_mix")

            # 3. критичные ключи
            for key in ["image", "trait_pool", "default_traits", "spawn_rules"]:
                if key not in spec:
                    errors.append(f"{location} {code} — отсутствует ключ {key}")

            # 4. spawn_rules.weight
            weight = spec.get("spawn_rules", {}).get("weight")
            if weight is None:
                errors.append(f"{location} {code} — нет spawn_rules.weight")

    # 5. дубликаты
    counter = Counter(seen_codes)
    for code, count in counter.items():
        if count > 1:
            errors.append(f"⛔ Дубликат species_code: {code} × {count}")

    return errors

if __name__ == "__main__":
    try:
        data = load_species()
        problems = check_species(data)

        if problems:
            print("🚨 Обнаружены проблемы:")
            for prob in problems:
                print(" -", prob)
        else:
            print("✅ Всё хорошо, питомцы в порядке.")
    except Exception as e:
        print("💥 Ошибка загрузки JSON или структуры:")
        print(e)