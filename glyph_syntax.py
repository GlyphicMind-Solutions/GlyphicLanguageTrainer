# ./interpreter/glyph_syntax.py
# Created By: David Kistner (Unconditional Love)

#system imports
from typing import List, Dict, Any

#folder imports
from .glyph_dictionary_loader import get_dictionary
from .glyph_validator import validate_sequence, validate_roles


# ===============================
# Glyph Syntax Error Class
# ===============================
class GlyphSyntaxError(Exception):
    """Raised when a glyph sequence violates syntax constraints.
       nothing in class currently
    """
    pass

#ordering
ROLE_ORDER = [
    "actor",
    "action",
    "object",
    "modifier",
    "context",
]
#context order
CONTEXT_ORDER = [
    "place",
    "time",
    "emotion",
    "sensory",
    "social",
]

# ----------------
# Get Role
# ----------------
def _get_role(entry: Dict[str, Any]) -> str:
    roles = entry.get("roles", [])
    for r in ROLE_ORDER:
        if r in roles:
            return r
    return "context"

# -------------------
# Get Context Type
# -------------------
def _get_context_type(entry: Dict[str, Any]) -> str:
    category = entry.get("category", "")

    if category.startswith("context_place"):
        return "place"
    if category.startswith("context_time"):
        return "time"
    if category.startswith("context_emotion") or category.startswith("emotion_context"):
        return "emotion"
    if category.startswith("context_sensory") or category.startswith("sensory_context"):
        return "sensory"
    if category.startswith("context_social") or category.startswith("social_context"):
        return "social"

    return "unknown"

# --------------
# New Clause
# --------------
def _new_clause() -> Dict[str, Any]:
    return {
        "actor": None,
        "action": None,
        "object": None,
        "modifiers": [],
        "context": {
            "place": [],
            "time": [],
            "emotion": [],
            "sensory": [],
            "social": [],
        },
    }

# -----------------
# Parse syntax
# -----------------
def parse_syntax(glyphs: List[str]) -> Dict[str, Any]:
    validate_sequence(glyphs)
    validate_roles(glyphs)

    dictionary = get_dictionary()

    clauses: List[Dict[str, Any]] = []
    current = _new_clause()

    last_role_index = -1
    last_context_index = -1
    # ---------------
    # Flush Clause
    # ---------------
    def flush_clause():
        nonlocal current, last_role_index, last_context_index
        if (
            current["actor"] is not None
            or current["action"] is not None
            or current["object"] is not None
            or current["modifiers"]
            or any(current["context"][k] for k in current["context"])
        ):
            clauses.append(current)
        current = _new_clause()
        last_role_index = -1
        last_context_index = -1

    for g in glyphs:
        entries = dictionary.get_entry_by_glyph(g)
        if not entries:
            raise GlyphSyntaxError(f"Unknown glyph: {g}")
        entry = entries[0]
        role = _get_role(entry)

        if role in ("actor", "action"):
            if (
                current["actor"] is not None
                or current["action"] is not None
                or current["object"] is not None
                or current["modifiers"]
                or any(current["context"][k] for k in current["context"])
            ):
                flush_clause()

        role_index = ROLE_ORDER.index(role)
        if role_index < last_role_index:
            raise GlyphSyntaxError(
                f"Invalid ordering: {g} ({role}) appears after a later role within a clause."
            )
        last_role_index = role_index

        if role == "actor":
            if current["actor"] is not None:
                raise GlyphSyntaxError("Multiple actors in a single clause are not allowed.")
            current["actor"] = entry

        elif role == "action":
            if current["action"] is not None:
                raise GlyphSyntaxError("Multiple actions in a single clause are not allowed.")
            current["action"] = entry

        elif role == "object":
            if current["object"] is not None:
                raise GlyphSyntaxError("Multiple objects in a single clause are not allowed.")
            current["object"] = entry

        elif role == "modifier":
            current["modifiers"].append(entry)

        elif role == "context":
            ctx_type = _get_context_type(entry)
            if ctx_type == "unknown":
                raise GlyphSyntaxError(f"Unknown context type for glyph {g}")

            ctx_index = CONTEXT_ORDER.index(ctx_type)
            if ctx_index < last_context_index:
                raise GlyphSyntaxError(
                    f"Context out of order: {ctx_type} appears after later context within a clause."
                )
            last_context_index = ctx_index

            current["context"][ctx_type].append(entry)

    flush_clause()

    return {
        "clauses": clauses,
        "raw": glyphs,
    }

# ------------------
# Get Syntax Tree
# ------------------
def get_syntax_tree(glyphs: List[str]) -> Dict[str, Any]:
    return parse_syntax(glyphs)

# ------------------
# Valid order
# ------------------
def is_valid_order(glyphs: List[str]) -> bool:
    try:
        parse_syntax(glyphs)
        return True
    except Exception:
        return False

