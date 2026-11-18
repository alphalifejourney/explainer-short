# Template map: what to change where

The project has the same layout as the reference film. Most topics only need the **COPY block**, **video.json** and **CUES**. Touch panel code only when a step can't be shown truthfully with the panel it has.

| File | What it holds | Change for a new topic? |
|---|---|---|
| `video.json` | title + the 7 voice lines (ids fixed) | yes |
| `BRIEF.md` | topic, steps, words on cards + the fixed palette/fonts/easing/ban list | topic part only |
| `words.py` | Whisper word timings -> `assets/words.json` | no |
| `build_audio.py` | `CUES` (cue slot -> spoken word), `TRAVEL`, holds; mixes `proj/media/vo.wav`, writes `/*TM*/` | `CUES` words; `TRAVEL` rarely |
| `proj/index.html` | the film | `COPY` block; panels only if needed |
| `proj/STYLE.md` | the style's rules | no |

## COPY limits (in px at 1080 wide; over these, text leaves its card)

| Field | Size | Limit |
|---|---|---|
| `title` | 140 px Switzer 800 | 1 word, 8 characters. The `chip` sits at x=760, so a longer title runs under it |
| `subtitle` | 92 px | 16 characters |
| `chip` | 40 px pill | 8 characters |
| `labels[i]` | 54 px card label | 7 characters, 1 word |
| `icons[i]` | 68 px chip | one of `clone` (download arrow), `copy`/`folder` (folder), `check` (tick box), `render` (play), `file`, `mark` (asterisk). To add an icon, put a 32x32 viewBox line icon in `ICON` (stroke 2.6, round caps, `currentColor`) |
| `term[0]` | 40 px mono | 14 characters |
| `term[1]` | 27 px mono | 40 characters |
| `tree[i][1]` | 34 px mono, indented 0 / 56 / 112 px | 22 / 20 / 18 characters |
| `checks[i]` | 40 px mono, row has an "ok" pill at the right | 16 characters |
| `ready` | 48 px mono on the banner | 12 characters |
| `prompt[i]` | 68 px Switzer 800 | 14 characters per line |
| `file` | 44 px mono | 22 characters |
| `end` | 118 px | 14 characters |
| `endUrl` | 32 px mono pill | 46 characters |

After every COPY edit, check the draft contact sheet. Overflow shows up there right away.

## Cue slots (build_audio.py CUES -> what index.html does on that word)

Each slot name is fixed: index.html reads `TM.<scene>.<slot>`. Point each one at a word that is actually spoken in that line. `'!word'` matches the last occurrence instead of the first. Full list in the comment above `CUES`.

Timing rules `build_audio.py` enforces:
- The camera arrives on a card 0.15 s after its first word starts.
- The camera leaves 0.3 s after the card's last word.
- The end card holds 1.8 s after the last word.
- Whole length = the voice plus about 2 s.

## Panels (only when a step doesn't fit)

Each card's interior is one block in index.html, headed `// ----- <Name>: ... -----`, and animated in its block under `// ---------- BEATS`. To rebuild one, for example card 2 as a settings toggle list instead of a folder tree:

1. Keep the card, its `hd` (chip + label) and the 716 x 440 panel area at `left 32, top 128`.
2. Draw the new interior with `el(...)`, using only the palette consts (`NAVY, GREEN, TINT, G1..G5, TERM`).
3. In BEATS, drive it from that card's existing cue slots (`C2.copy`, `C2.skills`, `C2.folder`) so `build_audio.py` stays unchanged. Easing comes from BRIEF.md: `power3.out` for entrances, `back.out(2-3)` for pops, `steps(n)` for typing.
4. Typing uses a clip-path reveal: `typed(...)` + `type(e, t, dur, steps)`.
5. Run the pacing check. A panel that does nothing for over 1 s while the voice talks is a dead gap: give it a beat on a word.

### Example: a website how-to (no terminal, no files)

"How to order a cake on our website": Open, Pick, Check, Write, Pay.

- Card 1 (terminal): keep the dark panel, but type the site address (`term[0]` = `bakery.com`, `term[1]` = `/order`) and turn the progress bar into a page loading. No fake browser frame.
- Card 2 (tree): the menu path as the three rows (Cakes > Birthday > Chocolate).
- Card 3 (check): the two rows the customer confirms (size, pickup date), then the banner.
- Card 4 (prompt): the message box on the cake, typed as it is said.
- Card 5 (player): rebuild as checkout: two option tiles (pickup / delivery) instead of the four looks, the five dots as payment progress, a tick instead of play, and `COPY.file` = `Order confirmed` style text (or the order number format the site really shows).

## Camera

`K` (keyframes) at the bottom of the script follows the Z: wide (hook) -> clone -> copy -> check (dip) -> prompt -> render (wider) -> wide (CTA). It lands on `TM.<card>.a` and leaves at `TM.<card>.d`. You never edit it for a new topic.
