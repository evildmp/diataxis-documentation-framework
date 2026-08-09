#!/usr/bin/env python3
"""Inspect the embedded subset: list all glyphs, the cmap, and check
coverage for the actual rendered diagram text (quadrant labels uppercased,
plus axis/orientation labels in mixed case).

Usage (from repo root): python3 font-tools/inspect_glyphs.py
"""
from fontTools.ttLib import TTFont

EMB_PATH = "_static/skia-subset.woff2"

font = TTFont(EMB_PATH)

glyph_order = font.getGlyphOrder()
print(f"--- glyph count: {len(glyph_order)} ---")
print("glyph order:", glyph_order)
print()

cmap = font.getBestCmap()
print(f"--- cmap entries: {len(cmap)} ---")
for cp in sorted(cmap):
    ch = chr(cp)
    gname = cmap[cp]
    try:
        glyph = font["glyf"][gname]
        has_outline = glyph.numberOfContours != 0 if hasattr(glyph, "numberOfContours") else None
    except KeyError:
        has_outline = "MISSING"
    print(f"  U+{cp:04X} {ch!r} -> {gname} (outline={has_outline})")
print()

texts = {
    "TUTORIALS": "Tutorials",
    "EXPLANATION": "Explanation",
    "HOW-TO GUIDES": "How-to guides",
    "REFERENCE": "Reference",
    "Acquisition": "Acquisition",
    "Application": "Application",
    "Knowledge": "Knowledge",
    "Practice": "Practice",
}
print("--- coverage check ---")
for label, src in texts.items():
    missing = []
    for ch in label:
        cp = ord(ch)
        if cp not in cmap:
            missing.append(f"{ch!r}(U+{cp:04X} NOT IN CMAP)")
        else:
            gname = cmap[cp]
            try:
                g = font["glyf"][gname]
                if hasattr(g, "numberOfContours") and g.numberOfContours == 0:
                    missing.append(f"{ch!r}(U+{cp:04X} -> {gname} EMPTY)")
            except KeyError:
                missing.append(f"{ch!r}(U+{cp:04X} -> {gname} GLYPH MISSING)")
    status = "OK" if not missing else "MISSING: " + ", ".join(missing)
    print(f"  {label!r:20} (from {src!r}): {status}")
