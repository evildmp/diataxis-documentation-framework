"""Cases the extension must leave alone.

Removal only triggers between two CJK characters, so English prose, the
desirable CJK↔Latin space, ambiguous-width *letters* (European accents)
and literal content are all preserved.
"""

from __future__ import annotations


def _page(outdir) -> str:
    return (outdir / "index.html").read_text(encoding="utf-8")


def test_english_prose_keeps_its_spaces(build_html):
    out = build_html("Welcome\n=======\n\nIt works *well* today.\n")
    html = _page(out)
    assert "It works <em>well</em> today." in html


def test_english_wrapped_line_keeps_the_joined_space(build_html):
    # docutils keeps the source newline in the Text node; HTML renders it
    # as a space — the separator between two English words, not an
    # artificial gap, so the extension leaves it alone.
    out = build_html(
        "Welcome\n=======\n\n"
        "This is a long sentence\n*emphasis* in the middle.\n"
    )
    html = _page(out)
    assert "long sentence\n<em>emphasis</em> in the middle." in html


def test_cjk_to_latin_seam_keeps_the_space(build_html):
    # The space between CJK and Latin text is desirable typography
    # ("pangu" spacing); only CJK↔CJK seams are glued.
    out = build_html("欢迎\n=======\n\n中文 *English* 中文。\n")
    html = _page(out)
    assert "中文 <em>English</em> 中文。" in html


def test_latin_to_cjk_seam_keeps_the_space(build_html):
    out = build_html("欢迎\n=======\n\n配置 :code:`Python` 的环境。\n")
    html = _page(out)
    assert "配置 <code" in html
    assert "</code> 的环境。" in html


def test_cjk_em_dash_seam_is_glued(build_html):
    # —— is Ambiguous-width punctuation, but CJK prose uses it without a
    # space around it, so the seam facing it glues. (The space *after*
    # —— that is plain text, not a markup seam, is left alone.)
    out = build_html("欢迎\n=======\n\n它 *行之有效* —— 无论用户。\n")
    html = _page(out)
    assert "它<em>行之有效</em>—— 无论用户。" in html


def test_cjk_ellipsis_seam_is_glued(build_html):
    out = build_html("欢迎\n=======\n\n它 *行之有效* …… 无论用户。\n")
    html = _page(out)
    assert "它<em>行之有效</em>…… 无论用户。" in html


def test_european_accented_letters_keep_their_spaces(build_html):
    # Ambiguous-width *letters* (French é, Greek α) must not act as CJK,
    # or European prose around CJK markup would lose its spacing.
    out = build_html("欢迎\n=======\n\nDéjà *强调* déjà。\n")
    html = _page(out)
    assert "Déjà <em>强调</em> déjà。" in html


def test_wide_emoji_keeps_the_space(build_html):
    # 😀 is Wide but a symbol, not text: the space next to it reads fine.
    out = build_html("欢迎\n=======\n\n句子 😀 *强调* 😀 结尾。\n")
    html = _page(out)
    assert "句子 😀 <em>强调</em> 😀 结尾。" in html


def test_parsed_literal_is_untouched(build_html):
    # Whitespace is significant inside literal blocks (parsed literals
    # share the literal_block class), markup or not.
    rst = (
        "欢迎\n"
        "=======\n"
        "\n"
        ".. parsed-literal::\n"
        "\n"
        "   即它 *为什么* 有效\n"
    )
    html = _page(build_html(rst))
    assert "即它 <em>为什么</em> 有效" in html


def test_code_block_is_untouched(build_html):
    rst = (
        "欢迎\n"
        "=======\n"
        "\n"
        ".. code-block:: text\n"
        "\n"
        "   即它 *为什么* 有效\n"
    )
    html = _page(build_html(rst))
    assert "即它 *为什么* 有效" in html


def test_escaped_asterisk_and_literal_asterisk(build_html):
    # A literal asterisk is plain text; there is no seam, nothing to do.
    out = build_html("欢迎\n=======\n\n中文 \\* 此处为星号。\n")
    html = _page(out)
    assert "中文 * 此处为星号。" in html


def _plain_text(html: str) -> str:
    """HTML reduced to its text, for highlighted blocks split into spans."""
    import html as html_module
    import re

    return html_module.unescape(re.sub(r"<[^>]+>", "", html))


def test_doctest_block_is_untouched(build_html):
    # Pygments splits the literal into spans, so check the plain text.
    rst = (
        "欢迎\n"
        "=======\n"
        "\n"
        ">>> 即它 *为什么* 有效\n"
    )
    html = _page(build_html(rst))
    assert ">>> 即它 *为什么* 有效" in _plain_text(html)
