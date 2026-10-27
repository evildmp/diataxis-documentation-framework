"""The gettext builder must keep ``.pot`` msgids verbatim.

The pass runs at ``doctree-resolved``, which the gettext builder also
reaches (it extracts from the resolved doctree). The extension skips that
builder, so the catalogs are byte-for-byte what they would be without it —
translators keep seeing the artificial spaces in msgids, and the existing
msgstrs keep matching.
"""

from __future__ import annotations

from pathlib import Path

from extensions.cjkspace.tests.conftest import _build


def _pot_body(path: Path) -> str:
    """The catalog without its header block (which carries timestamps)."""
    content = path.read_text(encoding="utf-8")
    # The header is the first msgid "" block, terminated by a blank line.
    return content.split("\n\n", 1)[1]


def test_short_msgid_keeps_artificial_spaces(tmp_path: Path):
    rst = "欢迎\n=======\n\n即它 *为什么* 有效，而不是如何运作。\n"

    _app, out = _build(
        tmp_path,
        rst,
        buildername="gettext",
        extra_conf="gettext_compact = False",
    )

    pot = (out / "index.pot").read_text(encoding="utf-8")
    assert "即它 *为什么* 有效，而不是如何运作。" in pot
    assert "即它*为什么*有效" not in pot


def test_catalog_is_identical_with_and_without_extension(tmp_path: Path):
    # Newlines inside a source paragraph are part of the msgid too; the
    # extension must not have joined them away before extraction. Comparing
    # against an extension-less build covers wrapping/escaping exactly.
    rst = (
        "欢迎\n=======\n\n"
        "这是一个很长的句子，在行末换行\n"
        "*紧接着强调* 然后继续。\n"
        "\n"
        "句子。 **粗体** 结尾。\n"
    )

    _app, out_with = _build(
        tmp_path / "with",
        rst,
        buildername="gettext",
        extra_conf="gettext_compact = False",
    )
    _app, out_without = _build(
        tmp_path / "without",
        rst,
        buildername="gettext",
        extra_conf="gettext_compact = False",
        extensions=(),
    )

    with_pot = _pot_body(out_with / "index.pot")
    without_pot = _pot_body(out_without / "index.pot")

    assert with_pot == without_pot
    # Sanity-check the comparison is not vacuous.
    assert "在行末换行" in with_pot
    assert "*紧接着强调*" in with_pot
    assert "**粗体**" in with_pot
