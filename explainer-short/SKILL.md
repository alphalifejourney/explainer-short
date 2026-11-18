---
name: explainer-short
description: Make a 9:16 how-to / install / tutorial short (about 30-35 s) in the explainer-diagram format - white dot-grid, five cards in a Z, a wide tilted diagram the camera dives through card by card, every action landing on the spoken word, narrated by Chatterbox in a clone of your voice from a short sample (or its built-in voice if you have none). English narration. Use when the user says explainer-short, "explainer v1 style", or asks for a how-to / setup / install / tutorial short for Instagram Reels, TikTok or YouTube Shorts.
---

# explainer-short

Builds one 1080x1920 short in the **explainer-diagram v1** format. On 29-30 Oct 2026 it was tested as an Instagram trial reel on @alphalifejourney against four other versions: 462 views, 7 shares, 6 saves and 5.4 s average watch; the next best got 137 views.

`template/` is the project behind that film. It has no voice files: the voice step makes them, cloned from the user's sample when they give one.

## Before you start

This skill runs programs on the user's computer (a voice model, a video renderer), so it needs **Claude Code**. If the user wrote in a language other than English, settle the language question (below) first. Then check every item before doing anything else. If one is missing, **stop** and tell the user, in plain words, what is missing and how to add it.

| Needed | Claude app (website, desktop, phone) | Claude Code |
|---|---|---|
| Where it runs | **Not supported.** The app cannot run the voice model or the renderer. Tell the user to install Claude Code (claude.com/claude-code) and use the skill there. | Works. Install the skill in `~/.claude/skills/explainer-short/`. |
| bash | - | Mac and Linux have it. Windows: Git Bash (comes with Git for Windows, git-scm.com). Run the `bash` commands below in it |
| Node 20+ and npx | - | `node --version`. Missing: install from nodejs.org |
| HyperFrames CLI (fetched by npx) | - | `npx --yes hyperframes@0.8.181 --version` (the first run downloads it; say so). Needs internet |
| ffmpeg + ffprobe | - | `ffmpeg -version`. Missing: Windows `winget install Gyan.FFmpeg`, Mac `brew install ffmpeg`, Linux your package manager |
| Python 3.10 or 3.11 with Chatterbox and Whisper | - | `python -c "import torch, chatterbox, whisper, torchaudio"`. Missing: these are big downloads (several GB), so **ask before installing**. Use a fresh virtual environment. Make one environment at a fixed place with Python 3.11: `py -3.11 -m venv ~/.venvs/explainer-short` (Windows) or `python3.11 -m venv ~/.venvs/explainer-short` (Mac, Linux). Activation doesn't carry between commands, so from then on call its interpreter directly wherever this file says `python`: `~/.venvs/explainer-short/Scripts/python.exe` (Windows) or `~/.venvs/explainer-short/bin/python` (Mac, Linux); the same for `pip`. NVIDIA users (Windows, Linux): chatterbox-tts pins torch 2.6.0, so install that exact CUDA build **first**: `pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124`. Then everyone: `pip install chatterbox-tts openai-whisper`. Re-run the GPU check after: if it says cuda False on an NVIDIA machine, the CPU build slipped in; repeat the torch line. Command name: Windows `python` (`python3` there is a Microsoft Store stub); Mac and Linux usually `python3`, so use that wherever this file says `python` |
| A GPU (optional) | - | `python -c "import torch; print('cuda', torch.cuda.is_available(), 'mps', torch.backends.mps.is_available())"`. NVIDIA (CUDA, about 8 GB video memory): about 5-10 minutes for everything. Apple Silicon (MPS): the voice runs on the GPU but word timing runs on the CPU, so plan on 15-25 minutes, and close other apps on an 8 GB Mac. Without one it runs on CPU: it works, but plan on 30-45 minutes the first time (model downloads, voice 10-20 min, word timing, render). Tell the user which they have and the time before starting |
| A voice sample (optional) | - | 10-20 s of the user talking normally, one speaker, no music, any audio format. Step 3 converts it to `<project>/voice-sample.wav`. If the path they give doesn't exist, ask again. No sample: Chatterbox's built-in voice is used. Say so plainly, and never call it their voice |
| Internet at render time | - | Fonts (Fontshare Switzer, Google JetBrains Mono) and GSAP load from CDNs. Without them the render falls back to system fonts: stop and tell the user |
| Disk space | - | At least 10 GB free the first time (Python packages and models), about 1 GB per video after that |
| Hook writer (optional) | - | `viral-hook-writer` skill installed. Not a blocker: score with `references/hook.md` and say so |

Paths below: `K` = the folder that holds this SKILL.md (usually `~/.claude/skills/explainer-short`), `P` = the project folder. Always quote them (`"$K"`, `"$P"`): user folders often contain spaces.

**Language:** the narration, hook and cards are **English only** (Chatterbox and Whisper `small.en`). If the user writes in another language, answer them in their language, tell them the video itself will be in English, and ask whether that works before building. If English is not OK, stop: say this skill can only make English videos, and build nothing.

## Inputs (ask once, in one message, only what is missing)

- **Topic** and the **real steps** in order, with the actual names of the pages, buttons, menus, commands or settings. No invented features. For a website or app, ask for the link and, if you can't open it, screenshots of each step. For a tool, check its README or docs. Never guess a flow: if the steps are missing, ask for them.
- What the end card should point to (link, keyword, site).
- Their **voice sample** (see Before you start) and, if they want their own brand, **two colours**: ink (dark, for text and the terminal) and accent (a strong, mid-to-dark colour: it carries white ticks and text, so pale colours are refused). Default: navy #203953 + green #288034. If their accent looks pale (yellow, light orange, pastel), say up front it may be refused and that a darker shade will be suggested.
- Defaults if not given: English, about 30-35 s, default colours, their voice sample (or the built-in voice if they have none), no captions (the winner had none), post nothing.

## Step 1 - Hook gate (before anything is built)

Follow `references/hook.md`. Write at least 8 hooks. The **proof-claim** pattern that won the test must be among them, and it is the default: "<something real that was just made or done>. Here's how you <do it>." Score them all.

**The rule:** the chosen hook must score **9 or higher with no honesty flag**. Never round up. Show the ranked table in one short message and continue.

If two rounds of rewrites still have nothing at 9, stop rewriting: show the best three with their honest scores and let the user pick. (The hook that won the original test scored 7 on this rubric, so a strong hook can land below 9. The user decides; Claude never inflates a score.)

The proof-claim does not have to be about the video. It is any real, checkable result of the steps: "This cake was ordered in five taps. Here's how you do it." Use the video itself as the proof only when the topic is the tool that made it.

The hook becomes the first voice line, word for word.

## Step 2 - Script (7 lines, fixed shape)

The format has exactly seven scenes, ids fixed: `hook, clone, copy, check, prompt, render, cta`. The ids are slot names: on screen the cards say whatever `COPY.labels` says. Map the topic onto them:

| Slot | Card panel | Voice line shape (5-12 words; the hook up to 15) |
|---|---|---|
| hook | wide diagram + title | the hook |
| clone | terminal: command + argument + progress | "Step one. <do X> ..." |
| copy | three-row tree (folder, folder, file) | "Step two. ..." |
| check | two rows that get an "ok", then a banner | "Step three. Make sure A and B ..." |
| prompt | a field where two lines type as they are said | "Step four. Open X and say, <line 1> <line 2>." |
| render | player: pick a look, five dots, play, a file lands | "Step five. Pick ..., answer ..., and it <result>." |
| cta | pull out, end title, link pill | "It is completely free. Grab it from the link on screen." (or the user's CTA) |

- Topic with fewer than 5 steps: split one. More than 5: merge. Never change the card count.
- Numbers are spelled out ("Step one").
- Each line must contain the **cue words** that card animates on (the comment above `CUES` in `template/build_audio.py` lists them). Choose the words while you write.
- If a panel can't show a step truthfully, rebuild that panel's interior. Expect this for anything that isn't a software install (a website, an app, a shop): usually the terminal and the player. `references/template-map.md` explains how, with a website example. Card labels are one word of at most 7 characters ("Pay", not "Checkout"). A command longer than the terminal limits (`term[0]` 14, `term[1]` 40 characters): split it, `term[0]` = `/plugin`, `term[1]` = `install superpowers`, and put the full command in the caption. Count anything you claim ("20 skills") against the tool's README, or leave the number out.

## Step 3 - Project

```bash
bash "$K/scripts/new.sh" <slug> "<parent folder>"   # creates <parent>/video-<slug>/ (default: the current folder) and prints it
```

In `P`, first (if they apply):

- **Colours** (only if the user gave their own): `python "$K/scripts/set_colors.py" "$P" --ink "#RRGGBB" --accent "#RRGGBB"`. Shades and glows are derived for you. It refuses an ink too light for text, an accent too light for the white ticks on it (and suggests a darker one), or two equal colours: tell the user why and offer the suggestion.
- **Voice sample:** convert it (any format) and check its length:
  `ffmpeg -v error -y -i "<sample>" -ac 1 -ar 24000 "$P/voice-sample.wav"` then `ffprobe -v error -show_entries format=duration -of csv=p=0 "$P/voice-sample.wav"`. Under 5 s or over 30 s: ask for a better one (or trim to the cleanest 10-20 s).

Then:

1. **`video.json`**: title + the seven `vo` lines.
2. **`BRIEF.md`**: topic, steps, words on cards, CTA. Keep the fonts, easing and ban list exactly as they are; if you ran `set_colors.py`, write the two new colours in the palette line.
3. **`proj/index.html` -> `COPY` block** (top of the script): every word on screen. Respect the length limits in the comments, so text never overflows its card.

## Step 4 - Voice (Chatterbox: the user's clone, or the built-in voice)

```bash
cd "$P" && python "$K/scripts/gen-chatterbox.py" "$P"    # run in the background: ~2-4 min on a GPU, 10-20 min on CPU; one at a time
```

- It writes `assets/vo-<id>.wav`. Lines go one sentence at a time, each verified by Whisper with retakes, and the script is resumable.
- If a line still drops a word (Chatterbox often eats "Step"), redo it: `python "$K/scripts/gen-chatterbox.py" "$P" --only <id> --force`. Repeat until it comes back clean.
- Then run `cd "$P" && python words.py`. It prints what Whisper heard per line, with times, and writes `assets/words.json`. Read that output: every word of the script must be there.
- Edit `CUES` in `"$P"/build_audio.py`: keep the names, and set each to a word that is actually in that line **as Whisper heard it**, in the order they are spoken (the comment above `CUES` lists each card's cues in order and what each animates). Whisper often mishears names ("Claude" comes back as "clod"): use a plain word from that line instead. Run `cd "$P" && python build_audio.py`. It fails loudly, naming the line, if a cue word isn't heard.

## Step 5 - Render and check

```bash
bash "$K/scripts/render.sh" "$P" "$P/out/draft.mp4" draft
python "$K/scripts/pacing_check.py" "$P/out/draft.mp4" --end-hold 2     # must PASS
```

- Pacing must PASS: no dead gap over 1 s, nothing on screen under 0.3 s. If there's a dead gap, add a beat on a word inside it. If something flashes, shorten the move or use a soft pulse (`pulse(id, t, true)`).
- Look at stills before the final render: `ffmpeg -v error -y -i "$P/out/draft.mp4" -vf "fps=1/2,scale=360:-1,tile=6x3" -frames:v 1 "$P/out/contact.jpg"`, then read the image.
- Check that the title fits, that no card text is cut off, and that the end pill fits the width.

Then render the final:

```bash
bash "$K/scripts/render.sh" "$P" "$P/out/<slug>.mp4" high
python "$K/scripts/pacing_check.py" "$P/out/<slug>.mp4" --end-hold 2
python "$K/scripts/sync_check.py" "$P" "$P/out/<slug>.mp4"
```

- **sync_check** writes `<slug>-sync.jpg` with one frame per cue word. Read it: each frame must show what the word names. It also prints SCRIPT vs HEARD, and they must match word for word (contractions aside).
- Share copy under 10 MB for phones: `ffmpeg -v error -y -i "$P/out/<slug>.mp4" -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart "$P/out/<slug>-share.mp4"`.

## Step 6 - Deliver

Give the user the share copy (send it if this session has a file-sending tool, otherwise give its full path). Tell the user:
- the hook and its score
- the voice used (their clone, or the built-in voice)
- the length
- the pacing result and the sync result
- the file paths

Say plainly if any check failed or was skipped.

## Step 7 - Posting (only when the user asks, and only to the account they name)

The format won as an Instagram trial reel. `references/posting.md` has that setup: cover frame at 1.5 s, trial reel, not shared to feed, at most 5 hashtags, first comment carrying the link. If the user has a scheduler connected (for example Blotato), use it; otherwise hand them the file, cover and caption to post themselves. Confirm the account before the first post.

## Rules

- **Never change the look.** The only colour change allowed is `set_colors.py` (ink + accent). No other colours, no second accent, no captions, no cuts between cards (the camera always travels), no sentences on cards, no em dash, no "!", no emoji. The ban list is in `template/BRIEF.md` and `template/proj/STYLE.md`.
- **The hook gate is not optional:** 9+ with no honesty flag, or the user picks from the best three (Step 1). Never a flagged hook.
- **No invented features.** Every command, path and button on screen must be real for the topic.
- Every beat sits on a spoken word: edit `CUES`, never hand-type times into `index.html` (`build_audio.py` rewrites the `/*TM*/` block).
- The camera, packets and player are pure functions of time. Keep anything you add deterministic: no `Math.random`, no `Date`.
- Don't edit files in `"$K"/template/` while making a video; work in the project copy.
- Don't leave background processes running.
