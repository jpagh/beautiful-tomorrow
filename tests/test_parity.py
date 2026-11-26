#!/usr/bin/env python3
"""The palette is the source of truth; these tests enforce it.

They fail if a hand edit to a colourscheme, a Giallo theme or a generated
terminal theme drifts from palette/{night,light}.toml, if a contrast floor
regresses, or if the light theme stops being the night theme's hue.
"""
import json
import math
import re
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import generate  # noqa: E402
import spec  # noqa: E402

VARIANTS = ("night", "light")
KAK = {v: ROOT / "kakoune" / "colors" / f"beautiful-tomorrow-{v}.kak" for v in VARIANTS}
GIALLO = {v: ROOT / "giallo" / f"beautiful-tomorrow-{v}.json" for v in VARIANTS}
ZED = ROOT / "zed" / "themes" / "beautiful-tomorrow.json"
WAYBAR = ROOT / "waybar" / "beautiful-tomorrow-night.css"
ZED_VARIANT_NAMES = {
    "night": ("Beautiful Tomorrow Night", "dark"),
    "light": ("Beautiful Tomorrow Light", "light"),
}


def palette(name):
    with open(ROOT / "palette" / f"{name}.toml", "rb") as f:
        return tomllib.load(f)


def zed_themes():
    with ZED.open() as f:
        family = json.load(f)
    return family, {t["name"]: t for t in family["themes"]}


def hex_rgb(value):
    """Normalise a #rrggbb or #rrggbbaa colour string to lowercase rrggbb."""
    m = re.fullmatch(r"#([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?", value)
    if not m:
        raise AssertionError(f"invalid hex colour: {value!r}")
    return m.group(1).lower()


def faces(path):
    """{face: (fg, bg)} with default-valued slots as None."""
    out = {}
    for m in re.finditer(r"^face global ([\w.]+) (.*)$", path.read_text(), re.M):
        parts = m.group(2).split(",", 1)
        fg = re.search(r"rgb:([0-9A-Fa-f]{6})", parts[0])
        bg = re.search(r"rgb:([0-9A-Fa-f]{6})", parts[1]) if len(parts) > 1 else None
        out[m.group(1)] = (fg.group(1).lower() if fg else None,
                           bg.group(1).lower() if bg else None)
    return out


def css_rules(path):
    """[(selectors, declarations)] for the flat rules in a Waybar stylesheet."""
    text = re.sub(r"/\*.*?\*/", "", path.read_text(), flags=re.S)
    rules = []
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text):
        declarations = {}
        for declaration in body.split(";"):
            if ":" in declaration:
                key, value = declaration.split(":", 1)
                declarations[key.strip()] = value.strip()
        rules.append(([s.strip() for s in selectors.split(",")], declarations))
    return rules


def css_colour(value):
    m = re.search(r"#[0-9a-fA-F]{6}\b", value)
    return m.group(0)[1:].lower() if m else None


def palette_colours(p):
    """Every colour in a palette file, normalised to lowercase rrggbb."""
    out = {p[k] for k in ("background", "foreground", "cursor", "cursor_text",
                          "selection")}
    out |= set(p["syntax"].values())
    out |= set(p["ansi"].values())
    return out


def luminance(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def oklch(h):
    def lin(x):
        x /= 255
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (x ** (1 / 3) if x > 0 else -((-x) ** (1 / 3)) for x in (l, m, s))
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


class PaletteAgreementTest(unittest.TestCase):
    def test_role_faces_match_the_palette(self):
        for name in VARIANTS:
            p, f = palette(name), faces(KAK[name])
            for role, face_names in spec.ROLE_FACES.items():
                for face in face_names:
                    with self.subTest(variant=name, face=face):
                        self.assertIn(face, f, f"{face} missing from {KAK[name].name}")
                        self.assertEqual(f[face][0], p["syntax"][role],
                                         f"{KAK[name].name}: face {face} should be "
                                         f"palette syntax.{role}")

    def test_default_face_is_the_background_and_foreground(self):
        for name in VARIANTS:
            p, f = palette(name), faces(KAK[name])
            self.assertEqual(f["Default"], (p["foreground"], p["background"]))

    def test_ansi_slots_carry_the_editor_colours(self):
        for name in VARIANTS:
            p = palette(name)
            for slot, role in spec.SLOT_ROLE.items():
                with self.subTest(variant=name, slot=slot):
                    self.assertEqual(p["ansi"][str(slot)], p["syntax"][role],
                                     f"ANSI {slot} must be syntax.{role}")

    def test_giallo_carries_every_palette_colour(self):
        for name in VARIANTS:
            p = palette(name)
            text = GIALLO[name].read_text().lower()
            # Only the roles the editor theme actually paints: `aqua` is a
            # terminal-only colour here (light borrows it, no face uses it).
            wanted = [p["background"], p["foreground"]]
            wanted += [p["syntax"][role] for role in spec.ROLE_FACES]
            for colour in wanted:
                with self.subTest(variant=name, colour=colour):
                    self.assertIn(f"#{colour.lower()}", text,
                                  f"{GIALLO[name].name} never uses #{colour}")  # noqa: E501

    def test_giallo_files_are_valid_json(self):
        for name in VARIANTS:
            with GIALLO[name].open() as f:
                self.assertIsInstance(json.load(f), dict)

    def test_zed_theme_is_valid_family(self):
        family, themes = zed_themes()
        self.assertEqual(family.get("$schema"), "https://zed.dev/schema/themes/v0.2.0.json")
        self.assertEqual(family.get("name"), "Beautiful Tomorrow")
        self.assertTrue(family.get("author"))
        self.assertEqual(len(family["themes"]), len(VARIANTS))
        for variant, (theme_name, appearance) in ZED_VARIANT_NAMES.items():
            with self.subTest(variant=variant):
                self.assertIn(theme_name, themes)
                theme = themes[theme_name]
                self.assertEqual(theme["appearance"], appearance)
                style = theme["style"]
                for key, val in style.items():
                    if isinstance(val, str) and key != "background.appearance":
                        hex_rgb(val)
                for accent in style.get("accents", []):
                    hex_rgb(accent)
                for player in style["players"]:
                    for field in ("cursor", "background", "selection"):
                        hex_rgb(player[field])
                for capture, spec_val in style["syntax"].items():
                    with self.subTest(capture=capture):
                        if spec_val.get("color") is not None:
                            hex_rgb(spec_val["color"])
                        self.assertIn(spec_val.get("font_style"), (None, "normal", "italic", "oblique"))
                        self.assertIn(spec_val.get("font_weight"), (None, 100, 200, 300, 400, 500, 600, 700, 800, 900))

    def test_zed_editor_matches_the_palette(self):
        _, themes = zed_themes()
        for variant, (theme_name, _) in ZED_VARIANT_NAMES.items():
            p = palette(variant)
            style = themes[theme_name]["style"]
            with self.subTest(variant=variant):
                self.assertEqual(hex_rgb(style["editor.background"]), p["background"])
                self.assertEqual(hex_rgb(style["editor.foreground"]), p["foreground"])
                self.assertEqual(hex_rgb(style["players"][0]["selection"]), p["selection"])

    def test_zed_syntax_matches_the_palette(self):
        _, themes = zed_themes()
        for variant, (theme_name, _) in ZED_VARIANT_NAMES.items():
            p = palette(variant)
            syntax = themes[theme_name]["style"]["syntax"]
            for role, captures in spec.ZED_ROLE_SYNTAX.items():
                for capture in captures:
                    with self.subTest(variant=variant, capture=capture):
                        self.assertIn(capture, syntax, f"{capture} missing from {theme_name}")
                        self.assertEqual(hex_rgb(syntax[capture]["color"]), p["syntax"][role],
                                         f"{theme_name}: syntax.{capture} should be "
                                         f"palette syntax.{role}")

    def test_zed_terminal_matches_the_palette(self):
        _, themes = zed_themes()
        for variant, (theme_name, _) in ZED_VARIANT_NAMES.items():
            p = palette(variant)
            style = themes[theme_name]["style"]
            with self.subTest(variant=variant):
                self.assertEqual(hex_rgb(style["terminal.background"]), p["background"])
                self.assertEqual(hex_rgb(style["terminal.foreground"]), p["foreground"])
            for slot, key in spec.ZED_ANSI_SLOTS.items():
                with self.subTest(variant=variant, slot=slot):
                    self.assertEqual(hex_rgb(style[key]), p["ansi"][str(slot)],
                                     f"{theme_name}: {key} must match ANSI slot {slot}")

    def test_waybar_uses_only_the_night_palette(self):
        allowed = palette_colours(palette("night"))
        colours = set(re.findall(r"#[0-9a-fA-F]{6}\b", WAYBAR.read_text()))
        self.assertTrue(colours, "waybar stylesheet has no colours")
        for colour in sorted(colours):
            with self.subTest(colour=colour):
                self.assertIn(colour[1:].lower(), allowed,
                              f"waybar uses {colour}, not in palette/night.toml")

    def test_waybar_bar_and_blocks_match_the_palette(self):
        p = palette("night")
        rules = css_rules(WAYBAR)

        def rule(selector):
            for selectors, declarations in rules:
                if selector in selectors:
                    return declarations
            self.fail(f"{selector} missing from {WAYBAR.name}")

        bar = rule("window#waybar")
        self.assertEqual(css_colour(bar["background-color"]), p["background"])
        self.assertEqual(css_colour(bar["color"]), p["foreground"])

        block = next((declarations for selectors, declarations in rules
                      if set(spec.WAYBAR_MODULES) <= set(selectors)), None)
        self.assertIsNotNone(block, "no single rule groups every Waybar indicator")
        self.assertEqual(css_colour(block["background-color"]),
                         p[spec.WAYBAR_MODULE_BACKGROUND])
        self.assertEqual(css_colour(block["color"]), p["foreground"])

    def test_waybar_states_use_the_palette_accents(self):
        p = palette("night")
        rules = css_rules(WAYBAR)

        def rule(selector):
            for selectors, declarations in rules:
                if selector in selectors:
                    return declarations
            self.fail(f"{selector} missing from {WAYBAR.name}")

        focused = rule("#workspaces button.focused")
        self.assertEqual(css_colour(focused["background-color"]),
                         p["syntax"]["function"])
        self.assertEqual(css_colour(focused["color"]), p["background"])

        urgent = rule("#workspaces button.urgent")
        self.assertEqual(css_colour(urgent["background-color"]),
                         p["syntax"]["constant"])
        self.assertEqual(css_colour(urgent["color"]), p["background"])


class QualityTest(unittest.TestCase):
    def test_contrast_floors(self):
        for name in VARIANTS:
            p = palette(name)
            bg = p["background"]
            self.assertGreaterEqual(contrast(p["foreground"], bg),
                                    spec.MIN_CONTRAST["foreground"])
            for role, colour in p["syntax"].items():
                with self.subTest(variant=name, role=role):
                    self.assertGreaterEqual(contrast(colour, bg), spec.MIN_CONTRAST[role],
                                            f"{name} {role} #{colour} on #{bg}")

    def test_light_keeps_the_night_hues(self):
        """The design property: light is the night palette with lightness inverted."""
        night, light = palette("night")["syntax"], palette("light")["syntax"]
        for role in night:
            c_night, h_night = oklch(night[role])
            c_light, h_light = oklch(light[role])
            if min(c_night, c_light) < 0.02:
                continue  # near-neutral: hue is noise
            drift = min(abs(h_night - h_light) % 360, 360 - abs(h_night - h_light) % 360)
            with self.subTest(role=role):
                limit = spec.HUE_DRIFT.get(role, spec.HUE_DRIFT["default"])
                self.assertLessEqual(drift, limit,
                                     f"{role}: {drift:.1f}° hue drift")

    def test_zed_tab_contrast(self):
        _, themes = zed_themes()
        for variant, (theme_name, _) in ZED_VARIANT_NAMES.items():
            style = themes[theme_name]["style"]
            active = hex_rgb(style["tab.active_background"])
            inactive = hex_rgb(style["tab.inactive_background"])
            bar = hex_rgb(style["tab_bar.background"])
            with self.subTest(variant=variant, pair="active/inactive"):
                self.assertGreaterEqual(
                    contrast(active, inactive), spec.ZED_TAB_MIN_CONTRAST,
                    f"{theme_name}: active tab #{active} vs inactive #{inactive}",
                )
            with self.subTest(variant=variant, pair="active/tab_bar"):
                self.assertGreaterEqual(
                    contrast(active, bar), spec.ZED_TAB_MIN_CONTRAST,
                    f"{theme_name}: active tab #{active} vs tab bar #{bar}",
                )

    def test_waybar_contrast(self):
        p = palette("night")
        bg = p["background"]
        block = p[spec.WAYBAR_MODULE_BACKGROUND]
        accent = p["syntax"]["function"]
        urgent = p["syntax"]["constant"]
        self.assertGreaterEqual(contrast(p["foreground"], bg),
                                spec.WAYBAR_MIN_CONTRAST["foreground"])
        self.assertGreaterEqual(contrast(p["foreground"], block),
                                spec.WAYBAR_MIN_CONTRAST["foreground"])
        self.assertGreaterEqual(contrast(p["syntax"]["comment"], bg),
                                spec.WAYBAR_MIN_CONTRAST["comment"])
        self.assertGreaterEqual(contrast(accent, block),
                                spec.WAYBAR_MIN_CONTRAST["accent"])
        self.assertGreaterEqual(contrast(bg, accent),
                                spec.WAYBAR_MIN_CONTRAST["accent"])
        self.assertGreaterEqual(contrast(bg, urgent),
                                spec.WAYBAR_MIN_CONTRAST["accent"])


class GeneratedOutputTest(unittest.TestCase):
    def test_generated_terminal_themes_are_current(self):
        for path, contents in generate.artifacts().items():
            with self.subTest(file=path.name):
                self.assertTrue(path.exists(), f"{path} missing")
                self.assertEqual(path.read_text(), contents,
                                 f"{path.name} is stale; run python3 generate.py")

    def test_ghostty_and_foot_agree(self):
        """The terminal themes must be the same palette in two syntaxes."""
        ghostty = {}
        for path in (ROOT / "terminal" / "ghostty").glob("*"):
            lines = path.read_text().splitlines()
            slots = {}
            for line in lines:
                m = re.match(r"palette = (\d+) = #([0-9a-f]{6})", line)
                if m:
                    slots[int(m.group(1))] = m.group(2)
                m = re.match(r"(background|foreground) = #([0-9a-f]{6})", line)
                if m:
                    slots[m.group(1)] = m.group(2)
            ghostty[path.name] = slots
        foot = {}
        section = None
        for line in (ROOT / "terminal" / "foot" / "theme.ini").read_text().splitlines():
            if line.startswith("[colors-"):
                section = line.strip("[]").replace("colors-", "")
                foot[section] = {}
                continue
            if section is None or "=" not in line or line.strip().startswith("#"):
                continue
            key, value = (x.strip() for x in line.split("=", 1))
            foot[section][key] = value
        pairs = {"Tomorrow Night": "dark", "Tomorrow": "light"}
        for theme, dark_or_light in pairs.items():
            g, f = ghostty[theme], foot[dark_or_light]
            self.assertEqual(g["background"], f["background"], theme)
            self.assertEqual(g["foreground"], f["foreground"], theme)
            regular = [g[i] for i in range(8)]
            bright = [g[i] for i in range(8, 16)]
            self.assertEqual(regular, [f[f"regular{i}"] for i in range(8)], theme)
            self.assertEqual(bright, [f[f"bright{i}"] for i in range(8)], theme)


if __name__ == "__main__":
    unittest.main()
