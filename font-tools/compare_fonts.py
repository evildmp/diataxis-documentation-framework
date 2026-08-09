#!/usr/bin/env python3
"""Compare the embedded Skia subset against the system Skia font.

Dumps OS/2, fvar, key name records, and gvar summary for both, side by
side, so you can confirm the subset preserved the axes and variation data
the diagram relies on (wght axis, gvar deltas).

Usage (from repo root): python3 font-tools/compare_fonts.py
"""
import os
import tempfile

from fontTools.ttLib import TTFont

EMB_PATH = "_static/skia-subset.woff2"
SYS_PATH = "/System/Library/Fonts/Supplemental/Skia.ttf"

emb = TTFont(EMB_PATH)
sys_font = TTFont(SYS_PATH)


def dump_os2(font, label):
    o = font["OS/2"]
    print(f"--- {label} OS/2 ---")
    print(f"  usWeightClass: {o.usWeightClass}")
    print(f"  fsSelection: {o.fsSelection} (bits: REG={bool(o.fsSelection & 64)} BOLD={bool(o.fsSelection & 32)} ITAL={bool(o.fsSelection & 1)})")
    print(f"  usWidthClass: {o.usWidthClass}")
    p = o.panose
    print(f"  panose: family={p.bFamilyType} serif={p.bSerifStyle} weight={p.bWeight} proportion={p.bProportion}")


def dump_fvar(font, label):
    print(f"--- {label} fvar ---")
    if "fvar" not in font:
        print("  NO fvar")
        return
    for ax in font["fvar"].axes:
        print(f"  axis {ax.axisTag}: min={ax.minValue} default={ax.defaultValue} max={ax.maxValue} flags={ax.axisNameID}")


def dump_gvar(font, label):
    print(f"--- {label} gvar ---")
    if "gvar" not in font:
        print("  NO gvar")
        return
    gv = font["gvar"]
    total_deltas = 0
    glyphs_with_deltas = 0
    empty_glyphs = 0
    for gname in font.getGlyphOrder():
        try:
            tupvar = gv.variations[gname]
        except KeyError:
            empty_glyphs += 1
            continue
        has_nonzero = False
        for t in tupvar:
            if t.coordinates:
                for pt in t.coordinates:
                    if pt != (0, 0):
                        has_nonzero = True
            total_deltas += 1
        if has_nonzero:
            glyphs_with_deltas += 1
    print(f"  total glyph entries in gvar: {len(gv.variations)}")
    print(f"  glyphs with non-zero deltas: {glyphs_with_deltas}")
    print(f"  glyphs with no gvar entry: {empty_glyphs}")
    print(f"  total tuple variations: {total_deltas}")


dump_os2(emb, "EMBEDDED")
dump_os2(sys_font, "SYSTEM")
print()
dump_fvar(emb, "EMBEDDED")
dump_fvar(sys_font, "SYSTEM")
print()
for label, font in (("EMBEDDED", emb), ("SYSTEM", sys_font)):
    print(f"--- {label} name key IDs ---")
    for nid in (1, 2, 4, 6, 16, 17, 21, 22, 25):
        v = font["name"].getDebugName(nid)
        print(f"  nameID {nid}: {v!r}")
print()
dump_gvar(emb, "EMBEDDED")
print()
dump_gvar(sys_font, "SYSTEM")
