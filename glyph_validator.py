# ./interpreter/glyph_validator.py
# Created By: David Kistner (Unconditional Love)

#system imports
from typing import List
#folder imports
from .glyph_dictionary_loader import get_dictionary

# =======================================
# Glyph Validation Error Class
# =======================================
class GlyphValidationError(Exception):
    """Raised when a glyph sequence fails validation.
       nothing in the class currently to validate errors
    """
    pass

# ----------------------
# Validate Sequence
# ----------------------
def validate_sequence(glyphs: List[str]) -> None:
    """
    Basic validation:
    - all glyphs must exist in the dictionary
    - sequence must not be empty
    """
    if not glyphs:
        raise GlyphValidationError("Empty glyph sequence is not allowed.")

    dictionary = get_dictionary()
    for g in glyphs:
        entries = dictionary.get_entry_by_glyph(g)
        if not entries:
            raise GlyphValidationError(f"Unknown glyph in sequence: {g}")

# --------------------
# Validate Roles
# -------------------
def validate_roles(glyphs: List[str]) -> None:
    """
    Role-level validation:
    - each glyph must have at least one role or be a known context/category
    - this does NOT enforce ordering (that is handled by glyph_syntax)
    """
    dictionary = get_dictionary()

    for g in glyphs:
        entries = dictionary.get_entry_by_glyph(g)
        if not entries:
            raise GlyphValidationError(f"Unknown glyph: {g}")
        entry = entries[0]
        roles = entry.get("roles", [])
        category = entry.get("category", "")

        if not roles and not category.startswith("context_") and not category.endswith("_context"):
            raise GlyphValidationError(
                f"Glyph {g} has no roles and is not a recognized context category."
            )

