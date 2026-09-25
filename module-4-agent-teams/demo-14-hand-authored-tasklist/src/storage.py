import json, os

class JsonStore:
    def __init__(self, root="data"):
        self.root = root

    def load(self, name):
        path = os.path.join(self.root, f"{name}.json")
        return json.load(open(path)) if os.path.exists(path) else {}

    def save(self, name, obj):
        os.makedirs(self.root, exist_ok=True)
        json.dump(obj, open(os.path.join(self.root, f"{name}.json"), "w"), indent=2)
