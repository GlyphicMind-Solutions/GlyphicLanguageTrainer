# interpreter/decoder_v2.py
# Created By: David Kistner (Unconditional Love)

#system imports
from typing import Dict, Any, List, Optional

#folder imports
from .glyph_syntax import parse_syntax

# -------------------
# Simplify Entry
# -------------------
def simplify_entry(entry: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if entry is None:
        return None

    return {
        "id": entry.get("id"),
        "glyph": entry.get("glyph"),
        "primary": entry.get("primary"),
        "category": entry.get("category"),
        "roles": entry.get("roles", []),
        "type": entry.get("type"),
        "article": entry.get("article"),
        "preposition_override": entry.get("preposition_override"),
    }

# ---------------------
# Simplify List
# ---------------------
def simplify_list(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [simplify_entry(e) for e in entries if e is not None]

# ---------------------
# Decode Glyphs
# ----------------------
def decode_glyphs_v2(glyphs: List[str]) -> Dict[str, Any]:
    tree = parse_syntax(glyphs)
    graph = build_semantic_graph(tree)
    text, sentences = realize_story(graph)

    return {
        "graph": graph,
        "text": text,
        "sentences": sentences,
        "raw": "".join(glyphs),
    }

# ----------------------------
# Build Semantic Graph
# ----------------------------
def build_semantic_graph(tree: Dict[str, Any]) -> Dict[str, Any]:
    clauses: List[Dict[str, Any]] = []

    raw_clauses = tree.get("clauses", [])
    for idx, c in enumerate(raw_clauses):
        clauses.append(_build_clause(c, idx))

    for i in range(1, len(clauses)):
        prev_id = clauses[i - 1]["id"]
        clauses[i].setdefault("relations", {})
        clauses[i]["relations"].setdefault("sequence_after", [])
        clauses[i]["relations"]["sequence_after"].append(prev_id)

    return {"clauses": clauses}

# ---------------------
# Build Clause
# ---------------------
def _build_clause(tree: Dict[str, Any], index: int) -> Dict[str, Any]:
    actor = simplify_entry(tree.get("actor"))
    action = simplify_entry(tree.get("action"))
    obj = simplify_entry(tree.get("object"))

    context_tree = tree.get("context", {})

    context = {
        "place": simplify_list(context_tree.get("place", [])),
        "time": simplify_list(context_tree.get("time", [])),
        "emotion": simplify_list(context_tree.get("emotion", [])),
        "sensory": simplify_list(context_tree.get("sensory", [])),
        "social": simplify_list(context_tree.get("social", [])),
    }

    return {
        "id": f"c{index}",
        "actor": actor,
        "action": action,
        "object": obj,
        "modifiers": simplify_list(tree.get("modifiers", [])),
        "context": context,
        "relations": {},
    }

# -----------------
# Realize Story
# -----------------
def realize_story(graph: Dict[str, Any]) -> (str, List[str]):
    clauses = graph.get("clauses", [])
    sentences: List[str] = []

    for idx, clause in enumerate(clauses):
        s = realize_clause(clause, idx)
        if s:
            sentences.append(s)

    text = " ".join(sentences).strip()
    return text, sentences

# -----------------
# Realize Clause
# -----------------
def realize_clause(clause: Dict[str, Any], index: int) -> str:
    actor = clause.get("actor")
    action = clause.get("action")
    obj = clause.get("object")
    ctx = clause.get("context", {})

    chunks: List[str] = []

    seq_prefix = realize_sequence_prefix(index)
    if seq_prefix:
        chunks.append(seq_prefix)

    if actor:
        chunks.append(realize_noun_phrase(actor))

    if action:
        chunks.append(realize_verb_phrase(action, obj))

    ctx_chunk = realize_context(ctx)
    if ctx_chunk:
        chunks.append(ctx_chunk)

    emo_chunk = realize_emotion_context(ctx)
    if emo_chunk:
        chunks.append(emo_chunk)

    sentence = " ".join(chunks).strip()
    if sentence and not sentence.endswith("."):
        sentence += "."
    return sentence

#Role Repositions
ROLE_PREPOSITIONS = {
    "motion": "to",
    "placement": "into",
    "surface": "on",
    "mental": "about",
    "transfer": "to",
}
#Category Articles
CATEGORY_ARTICLES = {
    "entity.person": "",
    "entity.proper": "",
    "entity.place": "the",
    "entity.object": "a",
    "context_place.store": "the",
}

# ---------------------------
# Realize Sequence Prefix
# ---------------------------
def realize_sequence_prefix(index: int) -> str:
    if index == 0:
        return ""
    return "Then"

# ---------------------
# Choose Article
# ---------------------
def choose_article(entry: Dict[str, Any]) -> str:
    if entry.get("article") is not None:
        return entry["article"]

    cat = entry.get("category", "")
    article = CATEGORY_ARTICLES.get(cat)
    if article is None:
        return ""
    return article

# ------------------------
# Realize Noun Phrase
# ------------------------
def realize_noun_phrase(entry: Dict[str, Any]) -> str:
    primary = entry.get("primary", "")
    article = choose_article(entry)
    if article:
        return f"{article} {primary}"
    return primary

# ----------------------
# Realize Verb Phrase
# ----------------------
def realize_verb_phrase(action: Dict[str, Any],
                        obj: Optional[Dict[str, Any]]) -> str:
    base = action.get("primary", "")
    verb = inflect_past(base)

    if obj:
        if obj.get("preposition_override"):
            prep = obj["preposition_override"]
        else:
            roles = action.get("roles", [])
            prep = ""
            for r in roles:
                if r in ROLE_PREPOSITIONS:
                    prep = ROLE_PREPOSITIONS[r]
                    break

        obj_phrase = realize_noun_phrase(obj)
        if prep:
            return f"{verb} {prep} {obj_phrase}"
        return f"{verb} {obj_phrase}"
    return verb

# -----------------------
# Realize Context
# -----------------------
def realize_context(ctx: Dict[str, Any]) -> str:
    chunks: List[str] = []

    times = ctx.get("time", [])
    if times:
        t_phrase = realize_time_phrase(times[0])
        if t_phrase:
            chunks.append(t_phrase)

    places = ctx.get("place", [])
    if places:
        p_phrase = realize_place_phrase(places[0])
        if p_phrase:
            chunks.append(p_phrase)

    return " ".join(chunks)

# ---------------------------
# Realize Emotion Context
# ---------------------------
def realize_emotion_context(ctx: Dict[str, Any]) -> str:
    emotions = ctx.get("emotion", [])
    if not emotions:
        return ""

    e = emotions[0]
    primary = e.get("primary")
    if not primary:
        return ""

    return f"feeling {primary}"

# --------------------------
# Inflect Past
# --------------------------
def inflect_past(verb: str) -> str:
    if not verb:
        return ""

    lower = verb.lower()

    irregular = {
        "go": "went",
        "come": "came",
        "run": "ran",
        "eat": "ate",
        "drink": "drank",
        "be": "was",
        "have": "had",
        "do": "did",
        "get": "got",
        "make": "made",
        "walk": "walked",
        "find": "found",
        "think": "thought",
        "set": "set",
        "put": "put",
    }
    if lower in irregular:
        form = irregular[lower]
        if verb[0].isupper():
            form = form.capitalize()
        return form

    if lower.endswith("e"):
        form = lower + "d"
    elif lower.endswith("y") and len(lower) > 1 and lower[-2] not in "aeiou":
        form = lower[:-1] + "ied"
    else:
        form = lower + "ed"

    if verb[0].isupper():
        form = form.capitalize()
    return form

# -------------------------
# Realize Time Phrase
# -------------------------
def realize_time_phrase(entry: Dict[str, Any]) -> str:
    cid = entry.get("id") or entry.get("primary", "")

    mapping = {
        "context.time.day.night": "tonight",
        "context.time.day.morning": "this morning",
        "context.time.day.afternoon": "this afternoon",
        "context.time.day.evening": "this evening",
        "context.time.cycle.daily": "every day",
        "context.time.cycle.weekly": "every week",
        "context.time.cycle.monthly": "every month",
        "context.time.duration.short": "for a short time",
        "context.time.duration.medium": "for a while",
        "context.time.duration.long": "for a long time",
    }

    phrase = mapping.get(cid)
    if phrase:
        return phrase

    primary = entry.get("primary")
    if primary and primary != cid:
        return primary

    return ""

# ------------------------
# Realize Place Phrase
# ------------------------
def realize_place_phrase(entry: Dict[str, Any]) -> str:
    cid = entry.get("id") or entry.get("primary", "")

    mapping = {
        "context.place.home": "at home",
        "context.place.work": "at work",
        "context.place.outside": "outside",
        "context.place.store": "at the store",
    }

    phrase = mapping.get(cid)
    if phrase:
        return phrase

    primary = entry.get("primary")
    if primary and primary != cid:
        return primary

    return ""

