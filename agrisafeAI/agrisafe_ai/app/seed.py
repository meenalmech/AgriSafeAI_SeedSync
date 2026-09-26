import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def load_chemical(name: str | None):
    if not name:
        return None
    data = json.loads((BASE / "data" / "chemicals.json").read_text(encoding="utf-8"))
    target = name.strip().lower()
    return next((x for x in data if x["name"].lower() == target), None)


def load_chemicals():
    return json.loads((BASE / "data" / "chemicals.json").read_text(encoding="utf-8"))
