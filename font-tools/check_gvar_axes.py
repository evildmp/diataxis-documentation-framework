#!/usr/bin/env python3
"""Inspect which axes the gvar tuples in the embedded subset actually
reference (wght vs wdth), and sanity-check that the default glyf instance
matches the expected wght by measuring the 'I' glyph stem width at a few
wght values.

Usage (from repo root): python3 font-tools/check_gvar_axes.py
"""
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib.instancer import instantiateVariableFont

EMB_PATH = "_static/skia-subset.woff2"
SYS_PATH = "/System/Library/Fonts/Supplemental/Skia.ttf"

emb = TTFont(EMB_PATH)
sys_font = TTFont(SYS_PATH)


def gvar_axes(font, label):
    gv = font["gvar"]
    axes_seen = {}
    for gname, tupvars in gv.variations.items():
        for t in tupvars:
            for tag, rng in (t.axes or {}).items():
                axes_seen.setdefault(tag, 0)
                axes_seen[tag] += 1
    print(f"--- {label} gvar tuple-axis usage ---")
    for tag, cnt in axes_seen.items():
        print(f"  axis {tag}: {cnt} tuples reference it")
    if not axes_seen:
        print("  (all tuples are shared/global, no per-axis peak tuples)")


gvar_axes(emb, "EMBEDDED")
gvar_axes(sys_font, "SYSTEM")
print()


def instantiate_and_measure(font, wght):
    f2 = instantiateVariableFont(font, {"wght": wght, "wdth": 1.0}, inplace=False)
    glyf = f2["glyf"]
    gname = "I"
    g = glyf[gname]
    pen = BoundsPen(f2.getGlyphSet())
    glyf.drawCoords(pen, g) if hasattr(glyf, "drawCoords") else f2.getGlyphSet()[gname].draw(pen)
    xMin, yMin, xMax, yMax = pen.bounds
    return xMax - xMin


for label, font in (("EMBEDDED", emb), ("SYSTEM", sys_font)):
    w_default = instantiate_and_measure(font, 1.0)
    w_light = instantiate_and_measure(font, 0.48)
    w_max = instantiate_and_measure(font, 3.2)
    print(f"--- {label} 'I' glyph width (xMax-xMin) ---")
    print(f"  wght=0.48 (Light):   {w_light}")
    print(f"  wght=1.0  (Regular): {w_default}")
    print(f"  wght=3.2  (Black):   {w_max}")
