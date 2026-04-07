# ./generator/meaning_model.py
# Created By: David Kistner (Unconditional Love)

#system imports
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any



# ======================
# Emotion Class
# ======================
@dataclass
class Emotion:
    type: str
    intensity: float

# ======================
# Context Class
# ======================
@dataclass
class Context:
    time: Optional[str] = None
    place: Optional[str] = None
    social: Optional[str] = None
    sensory: Optional[str] = None
    activity: Optional[str] = None

# =========================
# Structured Meaning Class
# =========================
@dataclass
class StructuredMeaning:
    actor: Optional[str]
    action: Optional[str]
    object: Optional[str]
    modifiers: List[str]
    emotion: Optional[Emotion]
    context: Context
    intent: str
    meta: Dict[str, Any]
    # ----------------------
    # to dict
    # ----------------------
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Flatten Emotion and Context dataclasses into dicts
        return d

