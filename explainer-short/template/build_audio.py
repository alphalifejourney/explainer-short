"""build_audio.py: lay the voiceover onto one track and time the picture to the words.

    python words.py        (once, after any voice line changes)
    python build_audio.py

Reads assets/vo-<scene>.wav and assets/words.json. Each card is timed so that:
  - the camera arrives on a card just as its line starts ("Step one" lands with the card),
  - every action inside the card fires on its word (CUES below),
  - the camera leaves a card only after its line has finished.
Writes proj/media/vo.wav and the TM constant + data-duration into proj/index.html.
"""
import json, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ['hook', 'clone', 'copy', 'check', 'prompt', 'render', 'cta']
# packet (and camera) travel time INTO each card
TRAVEL = {'clone': 0.85, 'copy': 0.5, 'check': 0.9, 'prompt': 0.45, 'render': 0.8}
FIRST_WORD_BEFORE_ARRIVAL = 0.15   # the first word starts this long before the camera settles
HOLD_AFTER_LINE = 0.3              # the camera stays this long after the last word
END_HOLD = 1.8                     # the end card holds this long after the last word
# word cues: name -> word to find (first match; '!' prefix = last match). Words are lowercase, no punctuation,
# as Whisper hears them (check assets/words.json); a prefix is enough ("ffmpeg" matches "ffmpeg").
# The NAMES are fixed slots that index.html uses; for a new topic change only the WORDS on the right:
#   hook.video     every card pulses (the proof word)         hook.how       the chip pops ("here's how")
#   clone.clone    terminal command types                     clone.url      argument types   clone.github  progress starts
#   copy.copy      row 2 slides in                            copy.skills    row 1 lights     copy.folder   row 3 lands
#   check.node     row 1 types, ok                            check.ffmpeg   row 2 types, ok  check.installed  green banner
#   prompt.open    field takes focus   prompt.code  card pulse   prompt.say  asterisk pops
#   prompt.make    line 1 starts typing                       prompt.motion  line 2 starts typing (send fires at line end)
#   render.style   a look gets picked  render.answer  dots start  render.questions  dots done  render.renders  play
#   cta.free       end title lands     cta.link  link pill lands   cta.screen  pill nudges
CUES = {
    'hook':   {'video': 'video', 'how': 'how'},
    'clone':  {'clone': 'clone', 'url': 'claude', 'github': 'github'},
    'copy':   {'copy': 'copy', 'skills': 'skills', 'folder': '!folder'},
    'check':  {'node': 'node', 'ffmpeg': 'ffmpeg', 'installed': 'installed'},
    'prompt': {'open': 'open', 'code': 'code', 'say': 'say', 'make': 'make', 'motion': 'motion'},
    'render': {'style': 'style', 'answer': 'answer', 'questions': 'questions', 'renders': 'renders'},
    'cta':    {'free': 'free', 'link': 'link', 'screen': 'screen'},
}

words = json.load(open(os.path.join(HERE, 'assets', 'words.json')))


def find(scene, target):
    ws = words[scene]
    hits = [w for w in ws if w['w'].startswith(target.lstrip('!'))]
    if not hits:
        raise SystemExit(f'cue word "{target}" not heard in {scene}: {" ".join(w["w"] for w in ws)}')
    return hits[-1] if target.startswith('!') else hits[0]


def r(x):
    return round(x, 3)


TM = {}
# hook: voice from 0.2 over the wide shot; the camera dives once the line is done
v = 0.2
h = {'v': v, 's': v + words['hook'][0]['s'], 'e': v + words['hook'][-1]['e']}
h['d'] = h['e'] + 0.1
TM['hook'] = h
prev_d = h['d']
for s in ORDER[1:-1]:
    a = prev_d + TRAVEL[s]
    v = a - FIRST_WORD_BEFORE_ARRIVAL - words[s][0]['s']
    sc = {'a': a, 'v': v, 's': v + words[s][0]['s'], 'e': v + words[s][-1]['e']}
    sc['d'] = sc['e'] + HOLD_AFTER_LINE
    TM[s] = sc
    prev_d = sc['d']
# cta: the pull out starts when Render's line ends, "free" lands as the title does
c = {'a': prev_d}
c['v'] = max(prev_d + 0.35, prev_d + 0.75 - find('cta', CUES['cta']['free'])['s'])
c['s'] = c['v'] + words['cta'][0]['s']
c['e'] = c['v'] + words['cta'][-1]['e']
TM['cta'] = c
for s in ORDER:
    for name, target in CUES[s].items():
        TM[s][name] = TM[s]['v'] + find(s, target)['s']
    TM[s] = {k: r(x) for k, x in TM[s].items()}
end = round(c['e'] + END_HOLD, 2)
TM['end'] = end


def dur(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


# one track: each line delayed to its voice start
inputs, filters = [], []
for i, s in enumerate(ORDER):
    inputs += ['-i', os.path.join(HERE, 'assets', f'vo-{s}.wav')]
    ms = int(round(TM[s]['v'] * 1000))
    filters.append(f'[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[a{i}]')
mix = ''.join(f'[a{i}]' for i in range(len(ORDER)))
filters.append(f'{mix}amix=inputs={len(ORDER)}:normalize=0,apad,atrim=0:{end},'
               f'afade=t=out:st={end - 0.3}:d=0.3,loudnorm=I=-14:TP=-1.5:LRA=7[out]')
out = os.path.join(HERE, 'proj', 'media', 'vo.wav')
os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filters),
                '-map', '[out]', '-ar', '48000', out], check=True)

p = os.path.join(HERE, 'proj', 'index.html')
html = open(p, encoding='utf-8').read()
html, n = re.subn(r'/\*TM\*/.*?/\*TM\*/', '/*TM*/' + json.dumps(TM, separators=(',', ':')) + '/*TM*/', html)
assert n == 1, 'no /*TM*/ marker in index.html'
html = re.sub(r'(id="root"[^>]*data-duration=")[0-9.]+', r'\g<1>' + str(end), html)
html = re.sub(r'(id="vo"[^>]*data-duration=")[0-9.]+', r'\g<1>' + str(end), html)
open(p, 'w', encoding='utf-8').write(html)

for s in ORDER:
    t = TM[s]
    print(f"{s:7s} " + '  '.join(f'{k} {x:.2f}' for k, x in t.items()))
print(f'total {end}s -> {out}')
