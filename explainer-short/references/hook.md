# Hook gate

The first line decides whether anyone watches. The rule: **no video until a hook scores 9/10 or higher with no honesty flag** (or, after two rewrite rounds, the user picks from the best three: step 6).

## What the test showed (IG trial reels, @alphalifejourney, 29-30 Oct 2026)

| Hook | Rubric score | Explainer views | Midnight views |
|---|---|---|---|
| "Claude made this whole video from one prompt. Here's how you set it up." | 7 | **462** | 137 |
| "No editor. No designer. Claude built this whole video. Here's how." | 9 | 87 | 131 |

The proof-claim hook won both pairs, though the rubric scored it lower. That was one post per version, and the 462 post had the evening slot, so it is a strong hint, not a law. It does mean the rubric overrates negation openers ("No X. No Y.") and underrates a concrete proof.

So **the proof-claim pattern is the default**, and every new hook is judged against it:

> **<Concrete proof: something real that was just made or done (the video itself only when the topic is the tool that made it)>. Here's how you <get the same result>.**

Why it works:
- the viewer is looking at the proof, so the claim is checked in the first second
- "here's how you set it up" promises a payoff the five steps deliver

## Process

1. If the `viral-hook-writer` skill is available, use it (Mode 1): business = the user's business, video topic = the short, viewer = who the user is talking to (ask if unclear).
2. Write at least 8 hooks from at least 5 formulas. At least one (ideally two) must be a proof-claim variant.
3. Score each one 0-2 on these five checks (total out of 10):
   - **Curiosity:** a gap the viewer wants closed.
   - **Clarity:** understood on first hearing, with no jargon.
   - **Speed:** spoken in under about 4.5 s and 15 words.
   - **Relevance:** the viewer sees what it does for them.
   - **Proof / contrast:** something concrete and checkable (the video itself counts only when the topic is the tool that made it). Check any number against the source, or leave it out.
4. **Honesty flag:** any claim that isn't literally true of this video and this tool, a guarantee, or an invented number. A flag means the hook is out, whatever its score.
5. **Benchmark:** score the plain proof-claim version of this topic as well. To beat it, a different hook needs a higher score *and* a reason it would stop the scroll better.
6. Pick a hook at **9+** with no flag. If none reaches 9, rewrite and score again. After two rewrite rounds with nothing at 9, show the best three with honest scores and let the user pick. Never round up.
7. Show the user the ranked table (hook, five scores, total) and the winner, then continue unless they asked to approve hooks.

## On screen

- The title (`COPY.title` + `COPY.subtitle`) names the topic in 2-4 words, for example "Install / Claude Video 2".
- The chip (`COPY.chip`) carries the promise, for example "5 steps".
- The proof word in the hook (`CUES.hook.video`) pulses every card. Pick the word that *is* the proof ("video", "app", "site").
