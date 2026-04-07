# ./tests/test_decoder_v2.py
# Created By: David Kistner (Unconditional Love)

#folder imports
from interpreter.decoder_v2 import decode_glyphs_v2

# -----------------------
# Test Simple Sequence
# -----------------------
def test_simple_sequence():
    # Example glyph string; adjust to match your actual glyphs
    glyphs = list("jack🚶‍➡️🏪")
    result = decode_glyphs_v2(glyphs)
    print("TEXT:", result["text"])
    print("SENTENCES:", result["sentences"])
    print("GRAPH:", result["graph"])

