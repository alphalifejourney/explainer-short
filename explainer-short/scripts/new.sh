#!/usr/bin/env bash
# new.sh: start an explainer-short project from the template.
# usage: bash new.sh <slug> [parent dir]   (default parent: the current folder)
set -e
SLUG=${1:?usage: new.sh <slug> [parent dir]}
PARENT=${2:-"$PWD"}
K=$(cd "$(dirname "$0")/.." && pwd)
DEST="$PARENT/video-$SLUG"
[ -e "$DEST" ] && { echo "exists: $DEST (pick another slug or delete it yourself)"; exit 1; }
mkdir -p "$DEST/assets" "$DEST/out" "$DEST/proj/media"
cp -r "$K/template/." "$DEST/"
# print a path every shell understands (Windows: C:/... rather than /c/...)
(cd "$DEST" && (pwd -W 2>/dev/null || pwd))
