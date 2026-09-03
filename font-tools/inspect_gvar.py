#!/usr/bin/env python3
"""Inspect the gvar tuples for a glyph to understand what the 8 variations
are, and compare embedded vs system for a representative accented glyph
('aacute').

Usage (from repo root): python3 font-tools/inspect_gvar.py
"""
from fontTools.ttLib import TTFont

EMB_PATH = "_static/skia-subset.woff2"
SYS_PATH = "/System/Library/Fonts/Supplemental/Skia.ttf"

embedded = TTFont(EMB_PATH)
system = TTFont(SYS_PATH)

print("=== fvar axes (system) ===")
for axis in system["fvar"].axes:
    print(f"  {axis.axisTag}: min={axis.minValue} default={axis.defaultValue} max={axis.maxValue}")

print()
print("=== gvar tuples for 'a' (system) ===")
sys_gvar = system["gvar"]
sys_cmap = system.getBestCmap()
gname_s = sys_cmap.get(ord("a"))
print(f"  glyph name: {gname_s}")
for i, var in enumerate(sys_gvar.variations.get(gname_s, [])):
    axes = var.axes
    print(f"  tuple {i}: axes={axes}")

print()
print("=== gvar tuples for 'aacute' (embedded) ===")
emb_gvar = embedded["gvar"]
emb_cmap = embedded.getBestCmap()
gname_e = emb_cmap.get(ord("á"))
print(f"  glyph name: {gname_e}")
for i, var in enumerate(emb_gvar.variations.get(gname_e, [])):
    axes = var.axes
    print(f"  tuple {i}: axes={axes}")
