# ./generator/encoder.py
# Created By: David Kistner (Unconditional Love)

#system imports
from typing import Optional, Dict, Any

#folder imports
from .fallback import encode_fallback
from .dict_utils import is_defined

# --------------
# Encode Term
# --------------
def encode_term(term_id: Optional[str], dictionaries: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Returns a dict with:
    - human
    - compact
    - tokens

    If the term is not defined in any dictionary, fallback is used.
    """
    if term_id is None:
        return None

    if not is_defined(term_id, dictionaries):
        return encode_fallback(term_id)

    upper = term_id.upper()

    return {
        "human": term_id,
        "compact": upper,
        "tokens": f"<{upper}>"
    }

