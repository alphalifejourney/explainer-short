"""words.py: word timings for each voiceover clip, so the picture can land on the word.

    python words.py

Transcribes assets/vo-<scene>.wav with Whisper (small.en, word timestamps) and writes
assets/words.json: {scene: [{"w": "clone", "s": 0.62, "e": 0.95}, ...]} (seconds into the clip).
Re-run after regenerating any voice line.
"""
import json, os, re, warnings

os.environ['TQDM_DISABLE'] = '1'
warnings.filterwarnings('ignore')
import whisper  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ['hook', 'clone', 'copy', 'check', 'prompt', 'render', 'cta']

import torch  # noqa: E402
model = whisper.load_model('small.en', device='cuda' if torch.cuda.is_available() else 'cpu')
out = {}
for s in ORDER:
    r = model.transcribe(os.path.join(HERE, 'assets', f'vo-{s}.wav'), language='en', word_timestamps=True)
    out[s] = [{'w': re.sub(r'[^a-z0-9]', '', x['word'].lower()), 's': round(x['start'], 3), 'e': round(x['end'], 3)}
              for seg in r['segments'] for x in seg['words']]
    print(s, ' '.join(f"{x['w']}@{x['s']:.2f}" for x in out[s]))
json.dump(out, open(os.path.join(HERE, 'assets', 'words.json'), 'w'), indent=1)
