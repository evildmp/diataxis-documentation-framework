#!/usr/bin/env python3
"""Inspect the embedded subset's tables, head/OS-2/name/fvar/gvar
presence. Useful to confirm the subset is still a variable font with
the wght axis intact.

Usage (from repo root): python3 font-tools/inspect_embedded.py
"""
from fontTools.ttLib import TTFont

EMB_PATH = "_static/skia-subset.woff2"

font = TTFont(EMB_PATH)
print(f"embedded font file: {EMB_PATH}")

print("\n--- tables present ---")
for tag in sorted(font.keys()):
    print(" ", tag)

print("\n--- head ---")
head = font["head"]
print(f"  macStyle: {head.macStyle} (bit1=bold)")

print("\n--- OS/2 ---")
os2 = font["OS/2"]
print(f"  usWeightClass: {os2.usWeightClass}")
print(f"  fsSelection: {os2.fsSelection} (bit6=REGULAR, bit5=BOLD)")

print("\n--- name (key records) ---")
for rec in font["name"].names:
    if rec.nameID in (1, 2, 4, 6, 16, 17, 21, 22, 25):
        try:
            print(f"  nameID {rec.nameID} ({rec.platformID},{rec.platEncID},{rec.langID}): {rec.toUnicode()!r}")
        except Exception as e:
            print(f"  nameID {rec.nameID}: <decode error {e}>")

print("\n--- fvar (variation axes) ---")
if "fvar" in font:
    fvar = font["fvar"]
    for ax in fvar.axes:
        print(f"  axis tag={ax.axisTag} min={ax.minValue} default={ax.defaultValue} max={ax.maxValue} flags={ax.axisNameID}")
    print("  named instances:")
    for inst in fvar.instances:
        coords = {k: v for k, v in inst.coordinates.items()}
        nm = font["name"].getDebugName(inst.subfamilyNameID)
        print(f"    nameID {inst.subfamilyNameID}: {nm!r} @ {coords}")
else:
    print("  NO fvar table -> static font, font-variation-settings has no effect")

print("\n--- gvar / HVAR / MVAR (variation data) ---")
for t in ("gvar", "HVAR", "MVAR", "avar"):
    print(f"  {t}: {'present' if t in font else 'absent'}")
