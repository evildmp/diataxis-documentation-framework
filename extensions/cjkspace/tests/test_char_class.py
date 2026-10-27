"""Unit tests for ``is_unspaced_char`` — the character class driving removal.

The extension removes a space only when both sides belong to a script
written without word spaces. That is Chinese/Japanese text (Han, kana,
bopomofo and their punctuation) — *not* Korean: Hangul separates words
with spaces, so a space next to Hangul is real and must be kept.
"""

from __future__ import annotations

import pytest

from extensions.cjkspace import is_unspaced_char


@pytest.mark.parametrize(
    "char",
    [
        # Han
        "中",  # CJK unified ideograph
        "日",
        "漢",  # used in Japanese too
        # Japanese kana
        "あ",  # hiragana
        "ア",  # katakana
        "ｶ",  # halfwidth katakana
        "・",  # katakana middle dot
        # Bopomofo
        "ㄅ",
        # CJK punctuation
        "。",
        "、",
        "！",
        "？",
        "（",
        "）",
        "「",
        "」",
        "【",
        "，",
        "１",  # fullwidth digit
        "％",
        "Ａ",  # fullwidth Latin letter: part of CJK text flow
        # Ambiguous-width punctuation used as CJK punctuation
        "—",  # em dash: ——
        "–",  # en dash
        "―",  # horizontal bar, Japanese dash
        "…",  # ellipsis: ……
        "‥",
        "“",
        "”",
        "·",
    ],
)
def test_unspaced_characters(char):
    assert is_unspaced_char(char)


@pytest.mark.parametrize(
    "char",
    [
        "",
        " ",
        "\u3000",  # ideographic space is whitespace, not text
        "A",
        "z",
        "0",
        ",",
        # Korean: words are separated by spaces
        "한",  # hangul syllable
        "글",
        "ᄒ",  # hangul jamo
        "ㅎ",  # hangul compatibility jamo
        "ﾡ",  # halfwidth hangul
        # Other scripts and symbols
        "é",  # Latin
        "α",  # Greek
        "Ж",  # Cyrillic
        "😀",  # wide, but an emoji
        "→",  # arrow
        "©",
    ],
)
def test_spaced_or_non_text_characters(char):
    assert not is_unspaced_char(char)
