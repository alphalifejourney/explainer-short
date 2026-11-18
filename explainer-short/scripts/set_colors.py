"""set_colors.py: swap the two brand colours in a project (ink and accent). Everything else stays.

    python set_colors.py <project-dir> --ink "#14213D" --accent "#E4572E"
    python set_colors.py <project-dir> --accent "#2B7EF9"     # change one, keep the other
    python set_colors.py <project-dir> --reset                # back to the default navy + green

Run it on the project copy (never on the skill's template/). It rewrites proj/index.html,
including the glows and shadows (rgba forms), and records the choice in proj/colors.json so a
second run starts from the right colours. Shades (terminal gradient, tint, button highlight and
shadow) are worked out from the two colours.

Rules it enforces:
- ink must be dark enough for white text on it and readable on white (contrast 4.5:1 or more)
- ink and accent must differ, and neither may equal white or one of the template's greys
"""
import argparse
import json
import os
import re
import sys

DEFAULT = {"ink": "#203953", "accent": "#288034"}
DEFAULT_SHADES = {"INK_LIGHT": "#284669", "ACC_TINT": "#E6F2E8", "ACC_LIGHT": "#8FD19A", "ACC_DARK": "#1F6A2A"}
# lighter tints of the ink used inside the dark terminal and player (dots, bars, thumbnails, text)
INK_TINTS = ["#3E5A7C", "#6F86A3", "#33506F", "#2E4C70", "#4A6789", "#B9C7DA"]
RESERVED = {"#FFFFFF", "#5B6478", "#8A93A8", "#C9CED9", "#E4E7EE", "#F4F6FA", "#F1F3F8", "#E3E6ED", "#CDD2DC"}


def rgb(h):
    h = h.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        sys.exit(f"not a 6-digit hex colour: #{h}  (example: #1B1B3A)")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def hexs(c):
    return "#" + "".join(f"{max(0, min(255, round(v))):02X}" for v in c)


def mix(a, b, t):
    """t=0 -> a, t=1 -> b"""
    return hexs([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


def luminance(h):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_on_white(h):
    return 1.05 / (luminance(h) + 0.05)


def tint_amount(shade):
    """How far a default ink tint sits from the default ink toward white (0..1)."""
    s, k = rgb(shade), rgb(DEFAULT["ink"])
    return sum((a - b) / (255 - b) for a, b in zip(s, k)) / 3


def palette(ink, accent):
    """Every colour the template uses for these two roles, keyed by role."""
    if {"ink": ink, "accent": accent} == DEFAULT:
        return {"ink": ink, "accent": accent, **DEFAULT_SHADES, **{f"INK_T{i}": h for i, h in enumerate(INK_TINTS)}}
    return {
        **{f"INK_T{i}": mix(ink, "#FFFFFF", tint_amount(h)) for i, h in enumerate(INK_TINTS)},
        "ink": ink,
        "accent": accent,
        "INK_LIGHT": mix(ink, "#FFFFFF", 0.06),     # top of the terminal gradient
        "ACC_TINT": mix(accent, "#FFFFFF", 0.88),   # pale accent background
        "ACC_LIGHT": mix(accent, "#FFFFFF", 0.45),  # highlight of the round button
        "ACC_DARK": mix(accent, "#000000", 0.22),   # shadow of the round button
    }


def rgba_key(h):
    r, g, b = rgb(h)
    return rf"rgba\(\s*{r}\s*,\s*{g}\s*,\s*{b}\s*,", f"rgba({r},{g},{b},"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--ink")
    ap.add_argument("--accent")
    ap.add_argument("--reset", action="store_true")
    a = ap.parse_args()

    html = os.path.join(a.project, "proj", "index.html")
    if not os.path.exists(html):
        sys.exit(f"no proj/index.html in {a.project}: pass the project folder made by new.sh")
    state = os.path.join(a.project, "proj", "colors.json")
    cur = json.load(open(state)) if os.path.exists(state) else dict(DEFAULT)

    if a.reset:
        new = dict(DEFAULT)
    else:
        if not (a.ink or a.accent):
            sys.exit("give --ink, --accent, or --reset")
        new = {"ink": a.ink or cur["ink"], "accent": a.accent or cur["accent"]}
    new = {k: hexs(rgb(v)) for k, v in new.items()}

    if new != DEFAULT:
        if new["ink"] == new["accent"]:
            sys.exit("ink and accent must be different colours")
        for k, v in new.items():
            if v in RESERVED:
                sys.exit(f"{k} {v} is white or one of the template's greys: pick another colour")
        c = contrast_on_white(new["ink"])
        if c < 4.5:
            sys.exit(f"ink {new['ink']} is too light (contrast {c:.1f}:1 on white, need 4.5:1). "
                     "Ink is used for text on white and behind white text: pick a darker colour.")
        ca = contrast_on_white(new["accent"])
        if ca < 3:
            darker = new["accent"]
            for _ in range(40):
                darker = mix(darker, "#000000", 0.05)
                if contrast_on_white(darker) >= 3:
                    break
            sys.exit(f"accent {new['accent']} is too light for the white ticks and text on it (contrast {ca:.1f}:1, need 3:1). "
                     f"A darker version that works: {darker}")

    old_p, new_p = palette(cur["ink"], cur["accent"]), palette(new["ink"], new["accent"])
    src = open(html, encoding="utf-8", newline="").read()
    subs = []  # (regex, replacement)
    for role in old_p:
        o, n = old_p[role], new_p[role]
        subs.append((re.escape(o), n))
        o_re, _ = rgba_key(o)
        _, n_txt = rgba_key(n)
        subs.append((o_re, n_txt))
    # two-step swap through placeholders so one colour can't overwrite another
    for i, (pat, _) in enumerate(subs):
        src = re.sub(pat, f"@@C{i}@@", src, flags=re.I)
    for i, (_, rep) in enumerate(subs):
        src = src.replace(f"@@C{i}@@", rep)
    open(html, "w", encoding="utf-8", newline="").write(src)
    json.dump(new, open(state, "w"), indent=1)
    print(f"ink {new['ink']}  accent {new['accent']}  -> {html}")


if __name__ == "__main__":
    main()
