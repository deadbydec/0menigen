import json
from collections import Counter

with open("products.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ids = [item["id"] for item in data]
names = [item["name"] for item in data]

id_counts = Counter(ids)
name_counts = Counter(names)

print("🔁 Дубликаты ID:")
for k, v in id_counts.items():
    if v > 1:
        print(f"ID {k} — {v} шт.")

print("\n🔁 Дубликаты NAME:")
for k, v in name_counts.items():
    if v > 1:
        print(f"NAME '{k}' — {v} шт.")
