import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def retrieve(query: str, top_k: int = 3) -> list[dict]:
    docs = json.loads((BASE / "data" / "knowledge.json").read_text(encoding="utf-8"))
    terms = set(re.findall(r"[a-zA-Z]+", query.lower()))
    scored = []
    for doc in docs:
        words = set(re.findall(r"[a-zA-Z]+", (doc["topic"] + " " + doc["text"]).lower()))
        score = len(terms & words)
        if score:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]
