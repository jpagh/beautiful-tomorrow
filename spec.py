"""Shared vocabulary for the generated artifacts and the tests."""

# Which Kakoune faces must carry a palette colour. Verified by the parity test,
# so a hand edit to a colourscheme that drifts from the palette fails the build.
ROLE_FACES = {
    "comment": ["comment"],
    "string": ["string"],
    "keyword": ["keyword", "mono"],
    "function": ["function", "MenuInfo", "link"],
    "variable": ["variable", "block"],
    "type": ["type", "module"],
    "constant": ["meta", "builtin", "title"],
    "orange": ["value", "attribute", "bullet"],
    "operator": ["operator", "bold", "italic"],
}

# ANSI slot -> the palette role it must match, when there is one. Slots 7 and 15
# are whites/greys with no editor equivalent; 8 is the comment colour.
SLOT_ROLE = {1: "constant", 2: "string", 3: "type", 4: "function",
             5: "keyword", 6: "aqua", 8: "comment"}

# Contrast floors against each variant's own background. Regression guards
# pinned to the current design, not quality claims: light-mode yellow is
# inherently weak on white (2.0:1) and stock Tomorrow light is no better.
MIN_CONTRAST = {
    "foreground": 7.0,
    "comment": 2.9,     # dim by design; that is the point of a comment colour
    "string": 4.6,
    "keyword": 4.2,
    "function": 3.9,
    "type": 1.95,       # yellow on white; the weakest role in the theme
    "constant": 4.4,
    "orange": 3.4,
    "operator": 2.45,
    "variable": 9.0,
    "aqua": 3.3,
}

# The design property this palette exists to preserve: a light colour's hue is
# the night colour's hue, only lighter. `aqua` gets more room because light has
# no cyan of its own -- it is borrowed from stock Tomorrow light.
HUE_DRIFT = {"default": 12.0, "aqua": 16.0}
