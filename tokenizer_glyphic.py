# generator/tokenizer_glyphic.py
# Created By: David Kistner (Unconditional Love)


#system imports
import re
from typing import List

#glyph header
GLYPHIC_HEADER_RE = re.compile(r"^### GLYPHIC\.[A-Z_]+$")
CTX_RE = re.compile(r"^CTX\.[a-zA-Z0-9_.]+$")


# --------------------------
# Tokenize Envelope
# --------------------------
def tokenize_envelope(envelope: str) -> List[str]:
    """
    Very simple tokenizer:
    - keeps GLYPHIC headers as tokens
    - keeps CTX.* glyphs as tokens
    - splits normal text on whitespace
    """
    tokens: List[str] = []
    for line in envelope.splitlines():
        line = line.strip()
        if not line:
            continue

        if GLYPHIC_HEADER_RE.match(line):
            tokens.append(line)
        elif CTX_RE.match(line):
            tokens.append(line)
        else:
            tokens.extend(line.split())

    return tokens

