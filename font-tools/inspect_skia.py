#!/usr/bin/env python3
"""Inspect the system Skia font: tables, head, OS/2, name records, fvar
axes and named instances, avar, gvar/HVAR/MVAR presence.

Usage (from repo root): python3 font-tools/inspect_skia.py
"""
from fontTools.ttLib import TTFont

SYS_PATH = "/System/Library/Fonts/Supplemental/Skia.ttf"

font = TTFont(SYS_PATH)

print(f"file: {SYS_PATH}")
print(f"tables: {sorted(font.keys())}\n")

print("--- head ---")
h = font["head"]
print(f"  unitsPerEm: {h.unitsPerEm}")
print(f"  macStyle: {h.macStyle} (bit1=bold)\n")

print("--- OS/2 ---")
o = font["OS/2"]
print(f"  usWeightClass: {o.usWeightClass}")
print(f"  fsSelection: {o.fsSelection} (bit6=REGULAR bit5=BOLD)\n")

print("--- name (family/subfamily) ---")
for rec in font["name"].names:
    if rec.nameID in (1, 2, 4, 6, 16, 17, 21, 22, 25):
        try:
            print(f"  nameID {rec.nameID} ({rec.platformID},{rec.platEncID},{rec.langID}): {rec.toUnicode()!r}")
        except Exception as e:
            print(f"  nameID {rec.nameID}: <{e}>")

print("\n--- fvar axes ---")
fvar = font["fvar"]
for ax in fvar.axes:
    print(f"  {ax.axisTag}: min={ax.minValue} default={ax.defaultValue} max={ax.maxValue} (nameID {ax.axisNameID}={font['name'].getDebugName(ax.axisNameID)!r})")

print("\n--- fvar named instances ---")
print(f"{'nameID':>6}  {'name':<20}  {'wght':>8}  {'wdth':>8}")
for inst in fvar.instances:
    nm = font["name"].getDebugName(inst.subfamilyNameID)
    w = inst.coordinates.get("wght")
    d = inst.coordinates.get("wdth")
    print(f"{inst.subfamilyNameID:>6}  {str(nm):<20}  {w:>8.4f}  {d:>8.4f}")

print("\n--- avar ---")
if "avar" in font:
    av = font["avar"]
    for tag, segs in av.segments.items():
        print(f"  {tag}: {len(segs)} segments")
        for s in segs:
            print(f"    {s}")
else:
    print("  absent")

print("\n--- gvar / HVAR / MVAR ---")
for t in ("gvar", "HVAR", "MVAR"):
    print(f"  {t}: {'present' if t in font else 'absent'}")
