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


def palette(name):
    with open(ROOT / "palette" / f"{name}.toml", "rb") as f:
        return tomllib.load(f)


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
