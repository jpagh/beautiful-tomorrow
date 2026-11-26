# Beautiful Tomorrow

One palette, six places: Kakoune, Giallo, Zed, Ghostty, Foot and Waybar. The
light and dark variants are the *same* colours adjusted for contrast — measured,
not eyeballed, and enforced by tests.

Derived from [Beautiful UI](https://github.com/swashata/vscode-beautiful-ui) by
Swashata Ghosh, which adapts Chris Kempson's [Tomorrow](https://github.com/chriskempson/tomorrow-theme).
MIT, see [LICENSE](LICENSE).

## What is here

```
palette/night.toml            the source of truth for the dark variant
palette/light.toml            the source of truth for the light variant
kakoune/colors/*.kak          Kakoune colourschemes (hand-authored detail)
giallo/*.json                 Giallo TextMate themes (hand-authored detail)
zed/themes/*.json             Zed theme family (hand-authored detail)
terminal/ghostty/*            generated: Ghostty themes
terminal/foot/theme.ini       generated: Foot [colors-dark] / [colors-light]
waybar/beautiful-tomorrow-night.css  Waybar theme (night only; no light/dark signal)
generate.py                   palette -> terminal themes
spec.py                       the shared vocabulary the tests enforce
tests/                        parity, contrast floors, hue consistency
```

The Kakoune, Giallo, Zed and Waybar files carry far more than a palette — faces,
UI colours, syntax captures, composited translucency, bar layout — so they are
hand-maintained. Every colour they share with the palette is checked against it,
so they cannot drift.

## The design rule

Night is canonical for the *dark* variant and light for the *light* one, and the
light variant is the night variant with lightness inverted. In OKLCH the light
syntax hues sit within 0.2–3.3° of their night counterparts, with unchanged
chroma; `tests/test_parity.py` fails if that stops being true. Stock Tomorrow
light, by comparison, drifts up to 11° and is roughly twice as saturated — it is a
separately designed sibling, not a light rendition of Tomorrow Night.

That is why the terminal follows the editor in light mode rather than the reverse.
Dark mode needs no such choice: the Kakoune theme and the terminal palette already
agreed, apart from rounding drift of up to 3/255 per channel, and the Kakoune
colours were snapped to the terminal's values.

## Options

| | night | light |
|---|---|---|
| background / foreground | `1d1f21` / `c5c8c6` | `ffffff` / `282a2e` |
| comment | `969896` | `959795` |
| string | `b5bd68` | `737935` |
| keyword | `b294bb` | `946ca1` |
| function, link | `81a2be` | `5884a9` |
| type | `f0c674` | `e9ad35` |
| constant | `cc6666` | `b83d3d` |
| orange / operator | `de935f` / `e9b36d` | `d2702b` / `e09432` |
| aqua | `8abeb7` | `3e999f` (borrowed from stock Tomorrow) |

## Use

**Kakoune** — copy or symlink `kakoune/colors/*.kak` into `~/.config/kak/colors`:

```kak
colorscheme beautiful-tomorrow-night
colorscheme beautiful-tomorrow-light
```

The names avoid shadowing Kakoune's bundled `tomorrow-night`. To follow the
terminal automatically, use [kakoune-tmux-light-dark](https://github.com/jpagh/kakoune-tmux-light-dark)
and name these two:

```kak
set-option global appearance_dark_theme  'beautiful-tomorrow-night'
set-option global appearance_light_theme 'beautiful-tomorrow-light'
```

**Giallo** — copy `giallo/*.json` into the directory named by `themes_path` in
`~/.config/giallo.kak/config.toml`, then `giallo-set-theme beautiful-tomorrow-night`.
The internal `name` of each file matches its filename, which Giallo requires.

**Zed** — copy or symlink `zed/themes/beautiful-tomorrow.json` into
`~/.config/zed/themes` and select the pair in `~/.config/zed/settings.json`:

```json
{
  "theme": {
    "mode": "system",
    "light": "Beautiful Tomorrow Light",
    "dark": "Beautiful Tomorrow Night"
  }
}
```

**Ghostty** — copy `terminal/ghostty/*` into Ghostty's `themes` directory and
select the pair:

```
theme = light:Tomorrow,dark:Tomorrow Night
```

**Foot** — copy the `[colors-dark]` and `[colors-light]` sections from
`terminal/foot/theme.ini` into your foot config. If you switch themes with
darkman, `initial-color-theme` belongs in `foot.ini`, because darkman owns
`state.ini`.

**Sway / Waybar** — copy or symlink `waybar/beautiful-tomorrow-night.css` into
`~/.config/waybar` and import it from `~/.config/waybar/style.css`:

```css
@import url("beautiful-tomorrow-night.css");
```

The theme is night-only: Sway and Waybar have no system light/dark signal of
their own, so there is no mode for a light bar to follow. The dark variant is
the canonical one, and it is what the bar uses.

Every indicator (clock, audio, network, CPU, memory, battery, tray, power)
sits directly on the bar background with `foreground` text; none of them draws
a block of its own. Only the focused workspace is a filled `function` block,
and an urgent workspace stays red. State is otherwise carried by text colour —
blue for active, `string` green for good, `constant` red for critical, `comment`
grey for inactive — so the bar reads as one surface rather than a row of
coloured blocks. Hovering a module gives it a temporary `selection` background.

## Changing a colour

```sh
$EDITOR palette/light.toml
python3 generate.py          # rewrite the terminal themes
python3 -m unittest discover -s tests -v
```

If the change also needs to reach the editors or the bar, edit the
`.kak`/`.json`/`.css` too — the tests will tell you exactly which face, capture
or block still disagrees with the palette.

## What the tests guarantee

- every face listed in `spec.ROLE_FACES` carries the palette's colour for its role;
- every Zed syntax capture listed in `spec.ZED_ROLE_SYNTAX` carries the palette's
  colour for its role, and Zed's editor and integrated terminal match the palette;
- every colour in the Waybar theme is in `palette/night.toml`, every indicator
  is transparent on the bar (only workspace focus/urgency is a filled block),
  and its text meets a contrast floor;
- each ANSI slot that has an editor equivalent (`red`, `green`, `yellow`, `blue`,
  `magenta`, `cyan`, `bright black`) is that same colour;
- Ghostty and Foot agree key for key, so the two terminals cannot drift apart;
- every palette colour the editor uses appears in the Giallo theme;
- contrast floors per role, and the light variant's hue stays within 12° of night;
- the generated terminal themes on disk match what `generate.py` would write.

## Known limitations

- **Light-mode yellow is weak.** `type` is `2.00:1` on white and `operator`
  `2.48:1`; `comment` is `2.94:1`. That is inherent to Tomorrow's light palette
  (stock is no better) and is preserved rather than "fixed", as changing it would
  change the look the theme is known for. The floors in `spec.py` pin today's
  values so they cannot slide further.
- **No aqua in the editor.** Neither variant uses cyan for a face; light borrows
  stock Tomorrow's `3e999f` for the terminal slot only.
- **The bar is night-only.** Sway and Waybar expose no system light/dark setting
  of their own, unlike the editors and terminals, so `waybar/` ships the dark
  variant only.
- **Giallo has no selection colour.** Its selection background comes from VS Code's
  own values, not from this palette.
