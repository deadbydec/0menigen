import json
import os

DATA_PATH = os.path.join("data", "random_events.json")

def load_random_events():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

RANDOM_EVENTS = load_random_events()