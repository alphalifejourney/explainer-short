"""gen-chatterbox.py: narrate a project's video.json with Chatterbox, cloning your voice sample.

    python gen-chatterbox.py <project-dir> [--only id1,id2] [--force] [--voice path/to/sample.wav]

Voice sample, first one found: --voice, the VOICE_SAMPLE environment variable,
<project-dir>/voice-sample.wav. With none, Chatterbox's built-in voice is used (and it says so).
A good sample: 10-20 s of you talking normally, one speaker, no music, WAV (SKILL.md Step 3 converts any format).

Writes assets/vo-<scene>.wav plus a .sha stamp, so a re-run skips lines that are already done.

How it avoids Chatterbox's failure mode (silently dropping the start or end of a long
generation): every line is generated ONE SENTENCE AT A TIME (a lead-in shorter than four
words, like "Reach.", is merged into the sentence after it), each sentence is transcribed
with Whisper and compared with the script, and a sentence that lost words is regenerated
(best of up to four takes). The sentences are then joined with a short natural pause and
the scene is peak-normalised.

Resumable: a scene whose WAV exists and whose stamp matches its text is skipped.
Voice settings: exaggeration 0.5, cfg 0.5. English only (Chatterbox and Whisper small.en).
Runs on an NVIDIA GPU (CUDA), Apple Silicon (MPS) or plain CPU. CPU works but is slow
(roughly 10-20 min for a 30 s video). Run one instance at a time: on a GPU, Chatterbox
plus Whisper need about 6-8 GB of video memory.
"""
import hashlib
import json
import os
import re
import sys
import tempfile
import time

os.environ["TQDM_DISABLE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

import torch  # noqa: E402
import torchaudio as ta  # noqa: E402
import whisper  # noqa: E402
from chatterbox.tts import ChatterboxTTS  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vo_norm import acceptable, compare  # noqa: E402

VOICE_ARG = None
VOICE_SAMPLE = None  # resolved in main(): --voice, $VOICE_SAMPLE, <project>/voice-sample.wav, else built-in voice
VOICE_NAME = "chatterbox:clone"
EXAGGERATION = 0.5
CFG_WEIGHT = 0.5
MAX_CHARS = 200
MIN_LEAD_WORDS = 4
GAP_SECONDS = 0.18
PEAK = 0.89
TAKES = 4

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True


def js_number(x):
    """Format a number the way JavaScript's String() does (1.0 -> "1")."""
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def chunks(text):
    sentences = [s.strip() for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()]
    merged = []
    for s in sentences:
        if merged and len(merged[-1].split()) < MIN_LEAD_WORDS:
            merged[-1] = merged[-1] + " " + s
        else:
            merged.append(s)
    out = []
    for c in merged:
        while len(c) > MAX_CHARS:
            cut = max(c.rfind(", ", 0, MAX_CHARS), c.rfind(": ", 0, MAX_CHARS), c.rfind("; ", 0, MAX_CHARS))
            if cut < 60:
                cut = c.rfind(" ", 0, MAX_CHARS)
            out.append(c[: cut + 1].strip())
            c = c[cut + 1 :].strip()
        if c:
            out.append(c)
    return out


def main():
    args = sys.argv[1:]
    project = args[0]
    only = set()
    force = "--force" in args
    global VOICE_ARG
    VOICE_ARG = args[args.index("--voice") + 1] if "--voice" in args else None
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))

    spec = json.load(open(os.path.join(project, "video.json"), encoding="utf-8"))
    assets = os.path.join(project, "assets")
    os.makedirs(assets, exist_ok=True)
    default_speed = js_number(spec.get("speed", 1))

    todo = []
    for scene in spec["scenes"]:
        if only and scene["id"] not in only:
            continue
        voice = scene.get("voice", spec.get("voice", VOICE_NAME))
        if not str(voice).startswith("chatterbox"):
            continue
        speed = js_number(scene["speed"]) if "speed" in scene else default_speed
        stamp = hashlib.sha1(f"{voice}|{speed}|{scene['vo']}".encode("utf-8")).hexdigest()
        wav = os.path.join(assets, f"vo-{scene['id']}.wav")
        sha = os.path.join(assets, f"vo-{scene['id']}.sha")
        fresh = (
            not force
            and os.path.exists(wav)
            and os.path.getsize(wav) > 40_000
            and os.path.exists(sha)
            and open(sha, encoding="utf-8").read().strip() == stamp
        )
        if fresh:
            print(f"  skip {scene['id']} (fresh)", flush=True)
            continue
        todo.append((scene, wav, sha, stamp))

    if not todo:
        print("ALL DONE (nothing to do)", flush=True)
        return

    global VOICE_SAMPLE
    cands = [VOICE_ARG, os.environ.get("VOICE_SAMPLE"), os.path.join(project, "voice-sample.wav")]
    VOICE_SAMPLE = next((c for c in cands if c and os.path.exists(c)), None)
    for src, path in (("--voice", VOICE_ARG), ("VOICE_SAMPLE", os.environ.get("VOICE_SAMPLE"))):
        if path and not os.path.exists(path):
            sys.exit(f"voice sample from {src} not found: {path}")
    print(f"Voice: {VOICE_SAMPLE or 'Chatterbox built-in voice (no sample found)'}", flush=True)
    if torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    if device == "cpu":
        print("No GPU found: running on CPU. This works but is slow (10-20 min for a 30 s video).", flush=True)
    print(f"Device: {device.upper()}  scenes to narrate: {len(todo)}", flush=True)
    t0 = time.time()
    model = ChatterboxTTS.from_pretrained(device=device)
    asr = whisper.load_model("small.en", device="cpu" if device == "mps" else device)
    print(f"Models loaded in {time.time() - t0:.1f}s", flush=True)
    gap = torch.zeros(1, int(GAP_SECONDS * model.sr))
    tmp = os.path.join(tempfile.gettempdir(), "chatterbox-take.wav")

    for scene, wav_path, sha_path, stamp in todo:
        ts = time.time()
        parts = []
        retakes = 0
        for i, piece in enumerate(chunks(scene["vo"])):
            best, best_score = None, -1.0
            for take in range(TAKES):
                w = model.generate(piece, audio_prompt_path=VOICE_SAMPLE, exaggeration=EXAGGERATION, cfg_weight=CFG_WEIGHT).cpu()
                ta.save(tmp, w, model.sr)
                heard = asr.transcribe(tmp, language="en", fp16=(device == "cuda"))["text"]
                ratio, missing = compare(piece, heard)
                score = ratio - 0.05 * len(missing)
                if score > best_score:
                    best, best_score = w, score
                if acceptable(ratio, missing):
                    break
                retakes += 1
                print(f"    retake {scene['id']} chunk {i} take {take + 1}: ratio {ratio:.2f} missing {' '.join(missing) or '-'}", flush=True)
            parts.append(best)
        joined = parts[0]
        for p in parts[1:]:
            joined = torch.cat([joined, gap, p], dim=-1)
        peak = float(joined.abs().max())
        if peak > 0:
            joined = joined * (PEAK / peak)
        ta.save(wav_path, joined, model.sr)
        with open(os.path.join(assets, f"vo-{scene['id']}.txt"), "w", encoding="utf-8") as f:
            f.write(scene["vo"])
        with open(sha_path, "w", encoding="utf-8") as f:
            f.write(stamp)
        dur = joined.shape[-1] / model.sr
        print(f"  {scene['id']}: {dur:.2f}s in {len(parts)} chunk(s), {retakes} retake(s)  (gen {time.time() - ts:.1f}s)", flush=True)

    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
