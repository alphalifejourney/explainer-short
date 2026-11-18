# explainer-diagram style

id: explainer-diagram
Best for: how something works, pipelines, systems, product flows, "what happens when you click send".
Mood: a crisp, living system diagram where every step is a little accent-coloured packet arriving somewhere.

## Palette (hex)
- ground: #FFFFFF with a dot grid rgb(226,226,232), 38 px
- ink: #203953 navy by default (text, the terminal and the player). Swappable with scripts/set_colors.py
- greys: #5B6478, #8A93A8, #C9CED9, #E4E7EE, #F4F6FA
- card border: #E3E6ED · wire track: #CDD2DC
- tint: #E6F2E8 (chips after a pulse; derived from the accent)
- accent: green #288034 by default (packets, lit wires, rings, the send and play buttons). Swappable with scripts/set_colors.py

## Type
- Display: Switzer 800, 54 px card labels, tracking -0.035em, line height 1
- Body: Switzer 700, tracking -0.03em
- One word per card. No sentences anywhere.
- Font links (paste into <head>; all fonts are free):
  <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=switzer@400,500,600,700,800&display=swap">

## Easing (numbers)
- card land: power3.out, 0.55 s, from 60 px down at scale 0.9
- label + chip: power3.out, 0.45 s, stagger 0.07 s
- pulse: scale 1.025 in 0.1 s, then back.out(3), 0.5 s; ring fades over 0.7 s (power2.out)
- wire draw: power2.inOut, 0.2 to 0.95 s (stroke-dashoffset)
- packet: power2.inOut, 0.45 to 0.9 s, with a 220 px comet trail
- camera: power3.inOut between cards, expo.inOut for the big pull out and the final fly in
- typing: steps(6 to 9)

## Motion rules
- Everything that happens is a packet leaving one card and arriving at the next.
- Each card pulses on arrival, on a 0.5 s beat.
- Wires draw themselves first, then carry packets. Elbows are rounded (40 to 72 px).
- The camera flies so the active card fills the frame, then pulls out to show the whole machine.
- The diagram plane tilts in 3D: it lands at 20 deg, tips back during the pull out, and leans with camera speed.
- A soft accent-coloured light pool follows the active card. Card shadows flash the accent colour on each pulse.

## Composition
- World is 3200 x 1800, two rows of cards: top row stepped heights, bottom row in a line.
- Cards: 36 px corners, white with a soft layered shadow, 68 px icon chip and one word.
- Tiny hand-drawn line icons (2.6 px stroke, round caps).
- Close shots fill the frame with one card; the wide shot shows every card at once.

## Ban list
- a second accent colour
- sentences or paragraphs on cards
- sharp corners or straight-elbow wires
- hard drop shadows
- cuts between cards (the camera always travels)
