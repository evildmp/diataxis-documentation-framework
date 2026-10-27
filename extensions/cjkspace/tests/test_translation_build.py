"""End-to-end: the real translation workflow this extension targets.

Sphinx re-parses every translated msgstr with the RST parser (the
``Locale`` transform), so translators write ``它 *有效* 得很`` — with the
spaces the markup needs to be recognised — directly in the catalog. The
rendered page then carries those spaces, until the final-stage pass
removes them.

Per language the outcome differs, because word spacing does: Chinese and
Japanese glue, Korean keeps its spaces (they are word boundaries). The
pair of Chinese tests builds the *same* project with and without the
extension, so the bug is reproduced without it and gone with it.
"""

from __future__ import annotations

from pathlib import Path

from extensions.cjkspace.tests.conftest import _build, _write_mo

INDEX_RST = "Welcome\n=======\n\nIt works *well*.\n"

CATALOG = {
    "Welcome": "欢迎",
    "It works *well*.": "它 *有效* 得很。",
}

CONF_EXTRA = 'locale_dirs = ["locale"]\ngettext_compact = False'


def _translated_build(
    tmp_path: Path,
    *,
    language: str = "zh_CN",
    rst: str = INDEX_RST,
    catalog: dict[str, str] = CATALOG,
    extensions=("extensions.cjkspace",),
):
    return _build(
        tmp_path,
        rst,
        language=language,
        extra_conf=CONF_EXTRA,
        extra_files={
            f"locale/{language}/LC_MESSAGES/index.mo": _write_mo(catalog)
        },
        extensions=extensions,
    )


def _page(outdir: Path) -> str:
    return (outdir / "index.html").read_text(encoding="utf-8")


def test_translated_msgstr_keeps_its_artificial_spaces_without_extension(tmp_path):
    _app, out = _translated_build(tmp_path, extensions=())
    html = _page(out)
    # The premise of the extension: the translated msgstr parses (its
    # spaces are what made the markup recognisable) and renders them.
    assert "它 <em>有效</em> 得很。" in html


def test_translated_msgstr_spaces_are_removed(tmp_path):
    _app, out = _translated_build(tmp_path)
    html = _page(out)
    assert "它<em>有效</em>得很。" in html
    assert "它 <em>" not in html
    assert "</em> 得很" not in html


def test_translated_title_is_glued(tmp_path):
    # Titles go through the same pass: the re-parsed translated title is
    # fixed before the page is written.
    catalog = {"Welcome": "欢迎 *到来* 吧", "It works *well*.": "它 *有效*。"}
    _app, out = _translated_build(tmp_path, catalog=catalog)
    html = _page(out)
    assert "欢迎<em>到来</em>吧" in html


def test_japanese_msgstr_spaces_are_removed(tmp_path):
    # Japanese, like Chinese, has no word spaces.
    rst = "Welcome\n=======\n\nIt is a book we read *while* cooking.\n"
    catalog = {
        "Welcome": "ようこそ",
        "It is a book we read *while* cooking.": "これは *重要* です。",
    }
    _app, out = _translated_build(
        tmp_path, language="ja", rst=rst, catalog=catalog
    )
    html = _page(out)
    assert "これは<em>重要</em>です。" in html


def test_korean_msgstr_keeps_word_spaces(tmp_path):
    # The reported regression (PR #174): in Korean the spaces around
    # *동안* are word boundaries, not markup padding, and must survive.
    rst = "Welcome\n=======\n\nIt is not a book we read *while* cooking.\n"
    catalog = {
        "Welcome": "환영",
        "It is not a book we read *while* cooking.": (
            "요리를 하는 *동안* 읽는 책이 아닙니다."
        ),
    }
    _app, out = _translated_build(
        tmp_path, language="ko", rst=rst, catalog=catalog
    )
    html = _page(out)
    assert "요리를 하는 <em>동안</em> 읽는 책이 아닙니다." in html
    assert "하는<em>동안</em>읽는" not in html
