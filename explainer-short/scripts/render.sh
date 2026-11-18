#!/usr/bin/env bash
# render.sh: render the project to MP4 with HyperFrames.
# usage: bash render.sh <project dir> <out.mp4> [draft|high]
set -e
DIR=$(cd "${1:?usage: render.sh <project dir> <out.mp4> [draft|high]}" && pwd)
OUT=${2:?need an output path}; Q=${3:-draft}
case "$OUT" in /*|?:*) ;; *) OUT="$PWD/$OUT";; esac
mkdir -p "$(dirname "$OUT")"
npx --yes hyperframes@${HF_VERSION:-0.8.181} lint "$DIR/proj"
npx --yes hyperframes@${HF_VERSION:-0.8.181} render "$DIR/proj" -o "$OUT" -q "$Q" -w "${HF_WORKERS:-auto}" --quiet
ffprobe -v error -show_entries format=duration:stream=width,height -of compact=p=0 "$OUT" | tr '\n' ' '; echo
${PYTHON:-$(command -v python || command -v python3)} -c "import os,sys;print('rendered:', sys.argv[1], round(os.path.getsize(sys.argv[1])/1e6,1), 'MB')" "$OUT"
