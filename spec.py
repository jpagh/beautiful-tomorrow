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

# Which Zed syntax captures must carry a palette colour. Verified by the parity
# test, matching the Kakoune ROLE_FACES above.
ZED_ROLE_SYNTAX = {
    "comment": ["comment", "comment.doc"],
    "string": ["string"],
    "keyword": ["keyword", "text.literal"],
    "function": ["function", "constructor", "label", "link_uri"],
    "variable": ["variable", "variable.parameter"],
    "type": ["type", "enum", "namespace", "string.escape"],
    "constant": ["tag", "property", "variable.special", "title", "preproc",
                 "punctuation.special"],
    "orange": ["number", "boolean", "constant", "attribute",
               "punctuation.list_marker", "link_text", "variant"],
    "operator": ["operator", "emphasis", "emphasis.strong", "selector"],
}

# ANSI slot -> Zed integrated terminal style key.
ZED_ANSI_SLOTS = {
    0: "terminal.ansi.black",
    1: "terminal.ansi.red",
    2: "terminal.ansi.green",
    3: "terminal.ansi.yellow",
    4: "terminal.ansi.blue",
    5: "terminal.ansi.magenta",
    6: "terminal.ansi.cyan",
    7: "terminal.ansi.white",
    8: "terminal.ansi.bright_black",
    9: "terminal.ansi.bright_red",
    10: "terminal.ansi.bright_green",
    11: "terminal.ansi.bright_yellow",
    12: "terminal.ansi.bright_blue",
    13: "terminal.ansi.bright_magenta",
    14: "terminal.ansi.bright_cyan",
    15: "terminal.ansi.bright_white",
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

# Minimum contrast between Zed's active tab and inactive tabs / tab bar so the
# current tab stays visually distinct in both variants.
ZED_TAB_MIN_CONTRAST = 1.3

# Waybar indicators that sit directly on the bar. There is no per-module
# background: the bar is one surface, and only the focused/urgent workspace
# blocks are filled. The bar is night-only because Sway and Waybar have no
# system light/dark signal of their own, so there is no mode for a light
# variant to follow. Verified against the single shared rule in
# waybar/beautiful-tomorrow-night.css.
WAYBAR_MODULES = [
    "#mode", "#idle_inhibitor", "#pulseaudio", "#wireplumber", "#network",
    "#cpu", "#memory", "#temperature", "#backlight", "#custom-battery",
    "#custom-battery-saver", "#battery", "#power-profiles-daemon", "#clock",
    "#tray", "#scratchpad", "#mpd", "#language", "#keyboard-state",
    "#custom-power",
]

# Contrast floors for the Waybar surface: foreground text on the bar, comment
# grey on the bar, foreground on the selection-coloured hover block, and dark
# text on the blue focus / red urgent blocks.
WAYBAR_MIN_CONTRAST = {
    "foreground": 6.5,
    "comment": 5.0,
    "accent": 4.0,
}
