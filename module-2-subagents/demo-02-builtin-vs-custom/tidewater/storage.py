"""JSON file storage."""
import json, os
DATA_DIR = os.environ.get("TIDEWATER_DATA", "data")

def load(name):
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def save(name, obj):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, f"{name}.json"), "w") as f:
        json.dump(obj, f, indent=2)
