#!/usr/bin/env python3
"""Scan all .po files and report the set of non-ASCII characters used in
translated (msgstr) strings, per locale and overall.

Used to decide the character coverage the embedded Skia subset needs.
Run this before rebuilding the subset to confirm the character set in
build_subset.sh covers everything translators have actually used.

Usage (from repo root): python3 font-tools/scan_po_chars.py [translation_dir]
"""
import os
import sys
from collections import defaultdict


def parse_po(path):
    """Yield (msgid, msgstr) pairs from a .po file (handles continuations)."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    state = None  # 'msgid' | 'msgstr'
    cur_id = []
    cur_str = []
    for line in lines:
        if line.startswith("msgid "):
            if state == "msgstr":
                yield "".join(cur_id), "".join(cur_str)
            cur_id = [line[len("msgid "):].strip().strip('"')]
            cur_str = []
            state = "msgid"
        elif line.startswith("msgstr "):
            cur_str = [line[len("msgstr "):].strip().strip('"')]
            state = "msgstr"
        elif line.startswith('"'):
            s = line.strip().strip('"')
            if state == "msgid":
                cur_id.append(s)
            elif state == "msgstr":
                cur_str.append(s)
    if state == "msgstr":
        yield "".join(cur_id), "".join(cur_str)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "translation"
    locales = sorted(
        d for d in os.listdir(root)
        if os.path.isdir(os.path.join(root, d))
    )
    per_locale = defaultdict(set)
    for loc in locales:
        d = os.path.join(root, loc, "LC_MESSAGES")
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".po"):
                continue
            for _mid, mstr in parse_po(os.path.join(d, fn)):
                if not mstr:
                    continue
                per_locale[loc].update(mstr)

    overall = set()
    for loc in locales:
        non_ascii = sorted(c for c in per_locale[loc] if ord(c) > 127)
        overall |= per_locale[loc]
        print(f"{loc}: {len(non_ascii)} non-ASCII chars")
        if non_ascii:
            print("  " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in non_ascii))
    print()
    non_ascii_overall = sorted(c for c in overall if ord(c) > 127)
    print(f"OVERALL: {len(non_ascii_overall)} non-ASCII chars")
    print("  " + " ".join(f"{c!r}(U+{ord(c):04X})" for c in non_ascii_overall))


if __name__ == "__main__":
    main()
