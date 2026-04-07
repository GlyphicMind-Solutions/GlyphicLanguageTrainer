# generator/dictionary_access.py
# Created By: David Kistner (Unconditional Love)

#system imports
import json
from pathlib import Path
from typing import Dict, Any

#local imports
from .config import DICTIONARY_DIR



# ------------------
# Load JSON
# ------------------
def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------
# Load All Dictionaries
# -----------------------
def load_all_dictionaries() -> Dict[str, Any]:
    """
    Loads all core Glyphic dictionaries into a single dict.
    Keys will match filenames without extension, e.g. 'actions', 'actors', etc.
    """
    dictionaries = {}
    for path in DICTIONARY_DIR.glob("*.json"):
        name = path.stem  # e.g. actions.json -> "actions"
        dictionaries[name] = load_json(path)
    return dictionaries

