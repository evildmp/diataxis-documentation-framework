"""Regression test: the embedded Skia font subset must cover every
character that the Latin-script translations actually use.

CJK locales (ja, ko, ru, zh_CN) use scripts Skia doesn't ship and fall
back to sans-serif by design, so they are excluded. Greek characters
that appear in some Latin-script .po files (e.g. in "Diátaxix") are
also excluded because Skia has no Greek coverage.

The test loads the woff2 referenced by ``_static/skia-font.css``, builds
its cmap, and asserts every character in the in-scope locales' msgstrs
is present. If a translator adds a new accented character that the
subset doesn't cover, this test fails instead of silently falling back
to sans-serif mid-word.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont


REPO_ROOT = Path(__file__).resolve().parents[3]
STATIC_DIR = REPO_ROOT / "_static"
CSS_PATH = STATIC_DIR / "skia-font.css"
FONT_WOFF2_PATH = STATIC_DIR / "skia-subset.woff2"
TRANSLATION_DIR = REPO_ROOT / "translation"

# Locales whose script Skia can render. CJK/Cyrillic locales fall back to
# sans-serif by design and are intentionally not asserted here.
LATIN_LOCALES = {"de", "es", "fr", "it", "pl", "pt_BR"}

# Codepoints that appear in Latin-script .po files but that the system
# Skia font does not cover (Greek letters used in "Diátaxix"/διάταξις,
# and a few Latin Extended-A letters with breve/overdot that Skia lacks).
# These are allowed to fall back to sans-serif; the test skips them.
SKIA_UNSUPPORTED = {
    0x00AD,  # soft hyphen (not in Skia)
    # Greek (used in "Diátaxix" etymology in fr/it/pl)
    0x03B4,  # δ
    0x03BE,  # ξ
    0x03C2,  # ς
    0x03C4,  # τ
    0x1FB0,  # ᾰ
    0x1FD0,  # ῐ
    0x0301,  # combining acute — only appears atop the Greek letters above
    # Latin Extended-A letters Skia doesn't ship (breve/overdot forms etc.)
    0x0108, 0x0109,  # Ĉ ĉ
    0x010A, 0x010B,  # Ċ ċ
    0x0114, 0x0115,  # Ĕ ĕ
    0x011C, 0x011D,  # Ĝ ĝ
    0x0120, 0x0121,  # Ġ ġ
    0x0124, 0x0125,  # Ĥ ĥ
    0x0126, 0x0127,  # Ħ ħ
    0x0128, 0x0129,  # Ĩ ĩ
    0x012C, 0x012D,  # Ĭ ĭ
    0x0132, 0x0133,  # Ĳ ĳ
    0x0134, 0x0135,  # Ĵ ĵ
    0x0138,  # ĸ
    0x014A, 0x014B,  # Ŋ ŋ
    0x014E, 0x014F,  # Ŏ ŏ
    0x015C, 0x015D,  # Ŝ ŝ
    0x0166, 0x0167,  # Ŧ ŧ
    0x0168, 0x0169,  # Ũ ũ
    0x016C, 0x016D,  # Ŭ ŭ
    0x0174, 0x0175,  # Ŵ ŵ
    0x0176, 0x0177,  # Ŷ ŷ
    0x017F,  # ſ
}


def _parse_po(path: Path):
    """Yield (msgid, msgstr) pairs from a .po file (handles continuations)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    state = None
    cur_id: list[str] = []
    cur_str: list[str] = []
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


def _load_embedded_cmap():
    """Load the woff2 referenced by _static/skia-font.css and return its best cmap."""
    assert FONT_WOFF2_PATH.is_file(), f"missing {FONT_WOFF2_PATH}"
    return TTFont(str(FONT_WOFF2_PATH)).getBestCmap()


def _latin_locale_chars():
    """Return {locale: set(chars)} for the in-scope Latin-script locales."""
    per_locale: dict[str, set[str]] = {}
    for loc in LATIN_LOCALES:
        d = TRANSLATION_DIR / loc / "LC_MESSAGES"
        if not d.is_dir():
            continue
        chars: set[str] = set()
        for po in sorted(d.glob("*.po")):
            for _msgid, msgstr in _parse_po(po):
                if msgstr:
                    chars.update(msgstr)
        per_locale[loc] = chars
    return per_locale


def test_css_file_exists():
    assert CSS_PATH.is_file(), f"missing {CSS_PATH}"


def test_translation_dir_exists():
    assert TRANSLATION_DIR.is_dir(), f"missing {TRANSLATION_DIR}"


def test_embedded_font_covers_latin_translations():
    """Every character in the Latin-script .po files must be in the embedded
    font's cmap (or be a known Skia-unsupported codepoint that falls back to
    sans-serif by design)."""
    cmap = _load_embedded_cmap()
    per_locale = _latin_locale_chars()

    failures: list[str] = []
    for loc, chars in sorted(per_locale.items()):
        for ch in sorted(chars):
            cp = ord(ch)
            if cp in SKIA_UNSUPPORTED:
                continue
            if cp < 0x80:
                # ASCII is always covered; skip to keep the failure list
                # focused on the diacritics this test exists to protect.
                continue
            if cp not in cmap:
                failures.append(
                    f"{loc}: {ch!r} U+{cp:04X} not in embedded font cmap"
                )

    assert not failures, (
        "Embedded Skia subset is missing characters used by translations "
        "(these would render with sans-serif fallback mid-word):\n  "
        + "\n  ".join(failures)
    )


@pytest.mark.parametrize("loc", sorted(LATIN_LOCALES))
def test_each_latin_locale_covered(loc):
    """Per-locale coverage check so a failure names the offending locale."""
    cmap = _load_embedded_cmap()
    d = TRANSLATION_DIR / loc / "LC_MESSAGES"
    if not d.is_dir():
        pytest.skip(f"no translations for {loc}")
    chars: set[str] = set()
    for po in sorted(d.glob("*.po")):
        for _msgid, msgstr in _parse_po(po):
            if msgstr:
                chars.update(msgstr)
    missing = [
        f"{ch!r} U+{ord(ch):04X}"
        for ch in sorted(chars)
        if ord(ch) >= 0x80
        and ord(ch) not in SKIA_UNSUPPORTED
        and ord(ch) not in cmap
    ]
    assert not missing, f"{loc}: missing from embedded font: {missing}"
