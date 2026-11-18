"""sync_check.py: prove the picture lands on the words.

    python sync_check.py <project dir> <video.mp4>

1. Transcribes the finished video with Whisper (small.en) and prints it under the script from video.json,
   so a dropped or masked word shows up.
2. Grabs one frame 0.35 s after every cue word in TM (proj/index.html) and tiles them into
   <video>-sync.jpg (4 across, in time order). Look at it: each frame must show the thing the word names.
"""
import json, os, re, subprocess, sys, tempfile, warnings

os.environ['TQDM_DISABLE'] = '1'
warnings.filterwarnings('ignore')
proj, video = sys.argv[1], sys.argv[2]
html = open(os.path.join(proj, 'proj', 'index.html'), encoding='utf-8').read()
TM = json.loads(re.search(r'/\*TM\*/(.*?)/\*TM\*/', html, re.S).group(1))
cues = []
for scene, d in TM.items():
    if isinstance(d, dict):
        for k, t in d.items():
            if k not in ('a', 'v', 's', 'e', 'd'):
                cues.append((t + 0.35, f'{scene}.{k}'))
cues.sort()
tmp = tempfile.mkdtemp()
frames = []
for i, (t, name) in enumerate(cues):
    f = os.path.join(tmp, f'{i:03d}.jpg')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', '-vf', 'scale=270:480', f], check=True)
    frames.append(f)
while len(frames) % 4:
    frames.append(frames[-1])
rows = len(frames) // 4
ins = sum((['-i', f] for f in frames), [])
lay = '|'.join(f'{(i % 4) * 270}_{(i // 4) * 480}' for i in range(len(frames)))
out = os.path.splitext(video)[0] + '-sync.jpg'
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f'xstack=inputs={len(frames)}:layout={lay}', out], check=True)
print('cue frames (left to right, top to bottom):')
for t, name in cues:
    print(f'  {t - 0.35:6.2f}s  {name}')
print('grid ->', out)
import whisper  # noqa: E402
import torch  # noqa: E402
m = whisper.load_model('small.en', device='cuda' if torch.cuda.is_available() else 'cpu')
r = m.transcribe(video, language='en')
script = ' '.join(s['vo'] for s in json.load(open(os.path.join(proj, 'video.json'), encoding='utf-8'))['scenes'])
print('\nSCRIPT :', script)
print('HEARD  :', r['text'].strip())
