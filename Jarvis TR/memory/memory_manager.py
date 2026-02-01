# memory/memory_manager.py
import json
import os
from threading import Lock
from datetime import datetime

MEMORY_PATH = "memory/memory.json"
_lock = Lock()


def _empty_memory() -> dict:
    """Return an empty memory structure."""
    return {
        "identity": {},
        "preferences": {},
        "relationships": {},
        "emotional_state": {}
    }


def load_memory() -> dict:
    """Load memory from disk, return empty if not exists or invalid."""
    if not os.path.exists(MEMORY_PATH):
        return _empty_memory()

    with _lock:
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return _empty_memory()
        except Exception:
            return _empty_memory()


def save_memory(memory: dict) -> None:
    """Save memory to disk safely."""
    if not isinstance(memory, dict):
        return

    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)

    with _lock:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)


def _recursive_update(target: dict, updates: dict) -> bool:
    """Recursively merge updates into target memory. Returns True if changed."""
    changed = False
    now = datetime.utcnow().isoformat() + "Z"

    for key, value in updates.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            continue

        if isinstance(value, dict) and "value" not in value:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
                changed = True
            if _recursive_update(target[key], value):
                changed = True
        else:

            entry = value if isinstance(value, dict) and "value" in value else {"value": value}
            if key not in target or target[key] != entry:
                target[key] = entry
                changed = True

    return changed


def update_memory(memory_update: dict) -> dict:
    """Merge LLM memory update into global memory and save."""
    if not isinstance(memory_update, dict):
        return load_memory()

    memory = load_memory()
    if _recursive_update(memory, memory_update):
        save_memory(memory)

    return memory
