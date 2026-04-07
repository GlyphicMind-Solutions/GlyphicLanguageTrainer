# ./interpreter/glyph_encoder.py
# Created By: David Kistner (Unconditional Love)

#system imports
from typing import Dict, Any, List, Optional
#folder imports
from .glyph_dictionary_loader import get_dictionary

# ----------------------
# Glyph from ID
# ----------------------
def _glyph_from_id(entry_id: str) -> Optional[str]:
    entry = get_dictionary().get_entry_by_id(entry_id)
    return entry.get("glyph") if entry else None

# -------------------
# Encode Clause
# -------------------
def encode_clause(structured: Dict[str, Any]) -> List[str]:
    glyphs: List[str] = []

    actor = structured.get("actor")
    if actor and actor.get("id"):
        g = _glyph_from_id(actor["id"])
        if g:
            glyphs.append(g)

    action = structured.get("action")
    if action and action.get("id"):
        g = _glyph_from_id(action["id"])
        if g:
            glyphs.append(g)

    obj = structured.get("object")
    if obj and obj.get("id"):
        g = _glyph_from_id(obj["id"])
        if g:
            glyphs.append(g)

    for m in structured.get("modifiers", []):
        if m.get("id"):
            g = _glyph_from_id(m["id"])
            if g:
                glyphs.append(g)

    context = structured.get("context", {})

    for ctx_key in ["place", "time", "emotion", "sensory", "social"]:
        for ctx in context.get(ctx_key, []):
            if ctx.get("id"):
                g = _glyph_from_id(ctx["id"])
                if g:
                    glyphs.append(g)

    return glyphs

# ----------------------
# Encode Meaning
# ----------------------
def encode_meaning(structured: Dict[str, Any]) -> str:
    """
    Multi-clause encoder:
    - if `clauses` is present: encode each clause in order and concatenate
    - else: treat `structured` as a single clause
    """
    glyphs: List[str] = []

    clauses = structured.get("clauses")
    if isinstance(clauses, list) and clauses:
        for clause in clauses:
            glyphs.extend(encode_clause(clause))
    else:
        glyphs.extend(encode_clause(structured))

    return "".join(glyphs)

