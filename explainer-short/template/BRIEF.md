# Brief: install Claude Video 2

- Style: explainer-diagram (see proj/STYLE.md). Brand colours replace the style's palette; rules stay.
- Size 1080 x 1920 (9:16), about 30-35 s, 30 fps, no loop.
- Topic: how to install github.com/ItsssssJack/claude-video-2 and make a motion graphic with Claude Code.
- Words: Install / Claude Video 2 / 5 steps. Cards (one word each): Clone, Copy, Check, Prompt, Render.
  Terminal pill shows the real commands. CTA: github.com/ItsssssJack/claude-video-2
- Palette: ground #FFFFFF + dot grid rgb(226,226,232) 38 px, ink #203953 (navy),
  accent #288034 (green) - ink and accent can be swapped with scripts/set_colors.py, greys #5B6478 #8A93A8 #C9CED9 #E4E7EE #F4F6FA, tint #E6F2E8.
- Fonts: Switzer 800/700 (Fontshare), JetBrains Mono 500/700 (Google). Both linked.
- Easing: card land power3.out 0.55 s; pulse 1.025 in 0.1 s then back.out(3) 0.5 s; wire draw power2.inOut;
  packet power2.inOut 0.9 s; camera power3.inOut between cards, expo.inOut for the dive in and the pull out.
- Safe zone: keep text out of the bottom 280 px and right 120 px where possible.
- Ban list: no hue-shifting gradients, no bloom, no linear easing on moving things, nothing scaling from zero,
  at most 6 words on screen (terminal text excepted), one accent, no fake chrome (no imitation browser or OS window frames; a simplified drawing of the user's real page inside a card is fine), no em dash, no "!", no emoji.
- Media: none (pure graphics).
