#!/usr/bin/env bash
# Rebuild _static/skia-subset.woff2 from the system Skia font.
#
# The diagram only ever uses wdth=1.0 (the default), so we pin wdth to 1.0
# via instantiateVariableFont after subsetting. This drops the wdth axis
# from fvar and removes all wdth-bearing gvar tuples (~6 of 8 per glyph),
# roughly halving gvar size while keeping the wght axis the diagram uses
# (0.6, 1.0, 1.25).
#
# Usage (from the repo root):
#   font-tools/build_subset.sh
#
# Requires: fonttools + brotli (see requirements.dev). The system font is
# expected at /System/Library/Fonts/Supplemental/Skia.ttf (macOS).
set -euo pipefail

SYSTEM_FONT="/System/Library/Fonts/Supplemental/Skia.ttf"
WOFF2_PATH="_static/skia-subset.woff2"
TMPDIR_LOCAL="${TMPDIR:-/tmp}"

if [[ ! -f "$SYSTEM_FONT" ]]; then
  echo "ERROR: system font not found at $SYSTEM_FONT" >&2
  exit 1
fi

SUBSET_TTF="$TMPDIR_LOCAL/skia_subset.ttf"
INSTANCED_TTF="$TMPDIR_LOCAL/skia_instanced.ttf"

# Character set: Basic Latin, Latin-1 Supplement, Latin Extended-A, plus
# straight apostrophe (U+0027, already in Basic Latin) and typographic
# apostrophe (U+2019). pyftsubset silently omits codepoints the source
# font doesn't have (e.g. many Latin Extended-A breve/overdot forms, Greek).
pyftsubset "$SYSTEM_FONT" \
  --output-file="$SUBSET_TTF" \
  --unicodes="U+0020-007F,U+00A0-00FF,U+0100-017F,U+2014,U+2018-201F" \
  --layout-features='*' \
  --no-subset-tables+=fvar,cvar,bsln,prop \
  --drop-tables+=DSIG \
  --no-hinting \
  --desubroutinize \
  --recalc-bounds \
  --recalc-average-width \
  --notdef-outline

# Pin wdth to 1.0 (the only value the diagram uses). This removes the wdth
# axis from fvar and prunes all wdth-bearing tuples from gvar.
python3 - "$SUBSET_TTF" "$INSTANCED_TTF" <<'PY'
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

src, dst = sys.argv[1], sys.argv[2]
font = TTFont(src)
# Only pin if wdth is actually present (idempotent on re-runs).
if any(a.axisTag == "wdth" for a in font["fvar"].axes):
    instantiateVariableFont(font, {"wdth": 1.0}, inplace=True)
font.save(dst)
PY

# Compress to woff2.
python3 - "$INSTANCED_TTF" "$WOFF2_PATH" <<'PY'
import sys
from fontTools.ttLib import TTFont

src, dst = sys.argv[1], sys.argv[2]
font = TTFont(src)
font.flavor = "woff2"
font.save(dst)
PY

echo "Wrote $WOFF2_PATH ($(wc -c < "$WOFF2_PATH") bytes)"
