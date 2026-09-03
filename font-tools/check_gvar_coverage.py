#!/usr/bin/env python3
"""Check which glyphs in the embedded subset have gvar wght deltas, and
that instanced outline widths at a given wght match the system font.

Specifically targets the glyphs used in the quadrant labels after the
uppercase transform, so we can confirm the subset's wght variation still
produces the same shapes as the full font.

Usage (from repo root): python3 font-tools/check_gvar_coverage.py
"""
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

EMB_PATH = "_static/skia-subset.woff2"
SYS_PATH = "/System/Library/Fonts/Supplemental/Skia.ttf"

embedded = TTFont(EMB_PATH)
system = TTFont(SYS_PATH)

# Text after uppercase transform
label_text = "TUTORIALS EXPLANATION HOW-TO GUIDES REFERENCE"
chars_needed = sorted(set(label_text))

print(f"Label text (uppercased): {label_text}")
print(f"Unique chars needed: {chars_needed}")
print()

emb_gvar = embedded["gvar"] if "gvar" in embedded else None
sys_gvar = system["gvar"] if "gvar" in system else None

emb_cmap = embedded.getBestCmap()
sys_cmap = system.getBestCmap()

print(f"{'Char':>4}  {'Name':<20}  {'Emb gvar?':>10}  {'Sys gvar?':>10}  {'Emb #tuples':>12}  {'Sys #tuples':>12}")
print("-" * 80)

for ch in chars_needed:
    cp = ord(ch)
    if cp == 0x20:  # space
        name = "<space>"
        emb_has = sys_has = "n/a"
        emb_n = sys_n = "-"
    elif cp == 0x2D:  # hyphen
        name = "<hyphen>"
        emb_gname = emb_cmap.get(cp)
        sys_gname = sys_cmap.get(cp)
        emb_has = "yes" if emb_gname in emb_gvar.variations else "NO"
        sys_has = "yes" if sys_gname in sys_gvar.variations else "NO"
        emb_n = len(emb_gvar.variations.get(emb_gname, []))
        sys_n = len(sys_gvar.variations.get(sys_gname, []))
    else:
        emb_gname = emb_cmap.get(cp, None)
        sys_gname = sys_cmap.get(cp, None)
        name = emb_gname or sys_gname or f"U+{cp:04X}"
        if emb_gname:
            emb_has = "yes" if emb_gname in emb_gvar.variations else "NO"
            emb_n = len(emb_gvar.variations.get(emb_gname, []))
        else:
            emb_has = "MISSING"
            emb_n = "-"
        if sys_gname:
            sys_has = "yes" if sys_gname in sys_gvar.variations else "NO"
            sys_n = len(sys_gvar.variations.get(sys_gname, []))
        else:
            sys_has = "MISSING"
            sys_n = "-"

    print(f"  {ch!r:>4}  {name:<20}  {emb_has:>10}  {sys_has:>10}  {str(emb_n):>12}  {str(sys_n):>12}")

# Now instantiate at wght 0.48 and compare outline widths
print()
print("=== Outline widths at wght=0.48 (Light) ===")
print(f"{'Char':>4}  {'Emb width':>10}  {'Sys width':>10}  {'Match?':>8}")
print("-" * 50)

for ch in chars_needed:
    cp = ord(ch)
    if cp == 0x20:
        continue
    emb_gname = emb_cmap.get(cp, None)
    sys_gname = sys_cmap.get(cp, None)
    if not emb_gname:
        print(f"  {ch!r:>4}  {'MISSING':>10}  {sys_gname or '-':>10}  {'-':>8}")
        continue

    # Instantiate embedded at wght 0.48. The embedded subset has wdth pinned
    # to 1.0 (no wdth axis), so only wght is supplied. The system font still
    # has both axes, so wdth=1.0 is passed explicitly to match.
    emb_axes = {a.axisTag for a in embedded["fvar"].axes}
    emb_inst = instantiateVariableFont(
        embedded,
        {"wght": 0.48, **({"wdth": 1.0} if "wdth" in emb_axes else {})},
    )
    sys_inst = instantiateVariableFont(system, {"wght": 0.48, "wdth": 1.0})

    emb_glyph = emb_inst["glyf"][emb_gname]
    sys_glyph = sys_inst["glyf"][sys_gname] if sys_gname else None

    if emb_glyph.numberOfContours == 0:
        emb_w = 0
    else:
        emb_w = emb_glyph.xMax - emb_glyph.xMin

    if sys_glyph is None or sys_glyph.numberOfContours == 0:
        sys_w = 0
    else:
        sys_w = sys_glyph.xMax - sys_glyph.xMin

    match = "YES" if emb_w == sys_w else "NO"
    print(f"  {ch!r:>4}  {emb_w:>10}  {sys_w:>10}  {match:>8}")
