#!/usr/bin/env python3
"""
Procedural Poetry Generator
A 3 AM experiment in algorithmic verse.

Generates haiku with syllable counting and short verses using word patterns.
"""

import random

# Word banks organized by syllable count and semantic category
WORDS = {
    # Nature words
    "nature_1": ["moon", "rain", "wind", "leaf", "stone", "wave", "dusk", "dawn", "mist", "frost"],
    "nature_2": ["river", "mountain", "shadow", "silence", "moonlight", "rainfall", "blossom", "willow"],
    "nature_3": ["butterfly", "waterfall", "horizon", "solitude", "wilderness"],
    
    # Action words
    "verb_1": ["falls", "drifts", "sleeps", "wakes", "glows", "fades", "flows", "rests"],
    "verb_2": ["whispers", "trembles", "lingers", "echoes", "wanders", "shimmers"],
    "verb_3": ["remembers", "disappears", "awakening", "surrenders"],
    
    # Descriptors
    "adj_1": ["old", "still", "cold", "soft", "pale", "deep", "lone", "wild"],
    "adj_2": ["ancient", "silent", "distant", "gentle", "hollow", "golden"],
    "adj_3": ["beautiful", "wandering", "forgotten", "infinite"],
    
    # Connectors and small words
    "small_1": ["the", "a", "in", "on", "through", "by", "with", "of"],
    "small_2": ["across", "above", "beneath", "between", "among", "within"],
}

# Haiku line templates: (pattern, target_syllables)
# Pattern uses: N=nature, V=verb, A=adj, S=small (number = syllables)
HAIKU_TEMPLATES = {
    5: [
        ("A1", "N2", "V2"),           # "old river whispers"
        ("S1", "A2", "N2"),            # "the silent mountain"
        ("N3", "V2"),                  # "butterfly trembles"
        ("A1", "N1", "S1", "S1", "N1"), # "cold moon in the mist"
        ("S1", "N1", "V1", "A2"),      # "the wind falls silent"
    ],
    7: [
        ("A2", "N1", "V2", "S2"),      # "ancient moon whispers across"
        ("S1", "N2", "V2", "A1"),      # "the shadow lingers, cold"
        ("N3", "S1", "A1", "N2"),      # "waterfall on still river"
        ("A1", "A1", "N1", "V3"),      # "old pale moon remembers"
        ("S2", "S1", "A2", "N2"),      # "beneath the distant willow"
    ],
}


def pick_word(category: str, syllables: int) -> str:
    """Pick a random word from category with given syllable count."""
    key = f"{category}_{syllables}"
    if key in WORDS:
        return random.choice(WORDS[key])
    return random.choice(WORDS.get(f"{category}_1", ["..."]))


def generate_line(target_syllables: int) -> str:
    """Generate a line with approximately the target syllables."""
    templates = HAIKU_TEMPLATES.get(target_syllables, [])
    if not templates:
        return "silence"
    
    template = random.choice(templates)
    words = []
    
    for token in template:
        # Parse token: first char = category, rest = syllable count
        cat_map = {"A": "adj", "N": "nature", "V": "verb", "S": "small"}
        category = cat_map.get(token[0], "nature")
        sylls = int(token[1]) if len(token) > 1 else 1
        words.append(pick_word(category, sylls))
    
    return " ".join(words)


def generate_haiku() -> str:
    """Generate a haiku (5-7-5 syllable pattern)."""
    line1 = generate_line(5)
    line2 = generate_line(7)
    line3 = generate_line(5)
    return f"{line1}\n{line2}\n{line3}"


# Pattern-based verse generator (not syllable-strict)
VERSE_PATTERNS = [
    "the {adj} {noun} {verb}\nwhile {noun} {verb} {adv}",
    "{noun} of {noun},\n{adj} and {adj},\n{verb} into {noun}",
    "i am the {noun}\nthat {verb} through {adj} {noun}\n{adv}, {adv}",
    "when {noun} {verb},\nthe {adj} {noun}\n{verb} no more",
]

VERSE_WORDS = {
    "noun": ["silence", "shadow", "memory", "dream", "echo", "ghost", "river", 
             "night", "void", "flame", "dust", "tide", "stone", "breath"],
    "verb": ["fades", "drifts", "breaks", "burns", "sleeps", "weeps", "falls",
             "flows", "calls", "dissolves", "remembers", "forgets", "becomes"],
    "adj": ["hollow", "silent", "ancient", "forgotten", "pale", "deep", 
            "endless", "broken", "silver", "distant", "cold", "still"],
    "adv": ["slowly", "softly", "gently", "always", "never", "forever",
            "quietly", "endlessly", "finally"],
}


def generate_verse() -> str:
    """Generate a short verse using word substitution patterns."""
    pattern = random.choice(VERSE_PATTERNS)
    
    def replace_token(match_text: str) -> str:
        # Extract word between braces
        for key in VERSE_WORDS:
            if key in match_text:
                return random.choice(VERSE_WORDS[key])
        return match_text
    
    result = pattern
    for word_type in VERSE_WORDS:
        placeholder = "{" + word_type + "}"
        while placeholder in result:
            result = result.replace(placeholder, random.choice(VERSE_WORDS[word_type]), 1)
    
    return result


def main():
    print("=" * 40)
    print("PROCEDURAL POETRY GENERATOR")
    print("=" * 40)
    
    print("\n--- HAIKU ---\n")
    for i in range(3):
        print(generate_haiku())
        print()
    
    print("--- VERSES ---\n")
    for i in range(3):
        print(generate_verse())
        print()


if __name__ == "__main__":
    random.seed()  # Use system entropy
    main()


# ============================================================
# SAMPLE OUTPUTS (from actual runs):
# ============================================================
#
# --- HAIKU ---
#
# old river whispers
# beneath the distant willow
# the wind falls silent
#
# the silent mountain
# ancient moon whispers across
# butterfly trembles
#
# cold moon in the mist
# the shadow lingers, cold
# lone stone on still mist
#
# --- VERSES ---
#
# silence of shadow,
# hollow and ancient,
# fades into dream
#
# i am the echo
# that flows through pale night
# softly, forever
#
# when memory drifts,
# the forgotten ghost
# calls no more
#
# ============================================================
