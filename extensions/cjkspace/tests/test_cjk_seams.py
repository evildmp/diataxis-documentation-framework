"""The extension strips artificial spaces between CJK text and inline markup.

Each case builds a one-page project whose ``index.rst`` contains CJK prose
with the spaces translators add around inline markup, then asserts the
rendered HTML has them removed. The English source *language* is used on
purpose for most cases: stripping is driven by the characters adjacent to
the seam, not by the configured language, so mixed-language content works
too.
"""

from __future__ import annotations

from extensions.cjkspace.tests.conftest import _build


def _page(outdir) -> str:
    return (outdir / "index.html").read_text(encoding="utf-8")


def test_emphasis_seams_are_glued(build_html):
    out = build_html(
        "欢迎\n=======\n\n即它 *为什么* 有效，而不是如何运作。\n"
    )
    html = _page(out)
    assert "即它<em>为什么</em>有效，而不是如何运作。" in html
    assert "即它 <em>" not in html
    assert "</em> 有效" not in html


def test_strong_seams_are_glued(build_html):
    out = build_html(
        "欢迎\n=======\n\n任何技能，都兼具 **实践表达** 与 **概念把握**。\n"
    )
    html = _page(out)
    assert "都兼具<strong>实践表达</strong>与<strong>概念把握</strong>。" in html


def test_closing_side_before_cjk_letter(build_html):
    # The docutils closer needs following whitespace/punctuation, so the
    # space after "**粗体**" is required to parse — and must not render.
    out = build_html("欢迎\n=======\n\n句子 **粗体** 中文。\n")
    html = _page(out)
    assert "<strong>粗体</strong>中文。" in html


def test_opening_side_after_cjk_letter(build_html):
    # Mirror case: the docutils opener must be preceded by whitespace when
    # the previous character is a CJK letter.
    out = build_html("欢迎\n=======\n\n即它 *为什么* 有效。\n")
    html = _page(out)
    assert "即它<em>为什么</em>有效。" in html


def test_space_after_cjk_full_stop_before_opener(build_html):
    # The space between 。 and the opening ** is the CommonMark-habit
    # workaround from the markdown-cjk-friendly README; in CJK there is
    # no space after a full stop.
    out = build_html("欢迎\n=======\n\n英文。 **粗体** 结尾。\n")
    html = _page(out)
    assert "英文。<strong>粗体</strong>结尾。" in html


def test_japanese_kana_seams_are_glued(build_html):
    # Japanese, like Chinese, runs its characters together.
    out = build_html("ようこそ\n========\n\nこれは *重要* です。\n")
    html = _page(out)
    assert "これは<em>重要</em>です。" in html


def test_japanese_punctuation_seam_is_glued(build_html):
    out = build_html("ようこそ\n========\n\nこれは終わり。 *重要* です。\n")
    html = _page(out)
    assert "これは終わり。<em>重要</em>です。" in html


def test_korean_word_spacing_is_kept(build_html):
    # Korean separates words with spaces: the spaces around *동안* are real
    # word boundaries, not markup padding (review comment on PR #174).
    out = build_html(
        "환영\n=====\n\n요리를 하는 *동안* 읽는 책이 아닙니다.\n"
    )
    html = _page(out)
    assert "요리를 하는 <em>동안</em> 읽는 책이 아닙니다." in html


def test_korean_spacing_between_marks_is_kept(build_html):
    out = build_html(
        "환영\n=====\n\n사용자의 *행동* 과 관련이 있습니다.\n"
    )
    html = _page(out)
    assert "사용자의 <em>행동</em> 과 관련이 있습니다." in html


def test_space_before_fullwidth_open_paren(build_html):
    # A fullwidth opening paren after the closing delimiter also forces a
    # space to parse; it must not survive rendering. (There is no markup
    # seam after （注）, so the extension does not touch that Text node.)
    out = build_html("欢迎\n=======\n\n句子 **粗体** （注）结尾。\n")
    html = _page(out)
    assert "<strong>粗体</strong>（注）结尾。" in html


def test_closing_side_before_cjk_punctuation(build_html):
    # The exact shape of the markdown-cjk-friendly example: emphasis
    # ending on a CJK full stop, immediately followed by CJK text.
    out = build_html("欢迎\n=======\n\n**这些星号。** 都是因为这个句子。\n")
    html = _page(out)
    assert "<strong>这些星号。</strong>都是因为这个句子。" in html


def test_double_space_is_fully_removed(build_html):
    out = build_html("欢迎\n=======\n\n即它  *为什么*  有效。\n")
    html = _page(out)
    assert "即它<em>为什么</em>有效。" in html


def test_literal_seams_are_glued(build_html):
    out = build_html("欢迎\n=======\n\n这是 ``内嵌代码`` 示例。\n")
    html = _page(out)
    assert "这是<code" in html
    assert "</code>示例。" in html


def test_wrapped_source_line_joins_without_space(build_html):
    # A source line wrapped right before the markup: the newline in the
    # Text node is an artificial space in exactly the sphinx-cjkspace
    # sense, and must be joined away between CJK characters.
    out = build_html(
        "欢迎\n=======\n\n"
        "这是一个很长的句子，在行末换行\n"
        "*紧接着强调* 然后继续。\n"
    )
    html = _page(out)
    assert "在行末换行<em>紧接着强调</em>然后继续。" in html


def test_fullwidth_space_is_whitespace(build_html):
    # U+3000 is whitespace both to docutils (\s) and to our regex; the
    # opener still parses after it, and it is stripped at both seams.
    out = build_html("欢迎\n=======\n\n即它　*为什么*　有效。\n")
    html = _page(out)
    assert "即它<em>为什么</em>有效。" in html


def test_whitespace_between_two_spans(build_html):
    # *甲* *乙*: the middle space is required for the two delimiter runs
    # not to fuse, but CJK wants the spans glued.
    out = build_html("欢迎\n=======\n\n**甲** **乙** 并列。\n")
    html = _page(out)
    assert "<strong>甲</strong><strong>乙</strong>并列。" in html


def test_text_between_two_spans_is_glued_both_sides(build_html):
    out = build_html("欢迎\n=======\n\n**甲** 和 **乙** 并列。\n")
    html = _page(out)
    assert "<strong>甲</strong>和<strong>乙</strong>并列。" in html


def test_element_with_children_supplies_its_edge(build_html):
    # A reference wraps its own Text child; the seam character is the
    # text the whole element renders at its edges, not its type.
    rst = (
        "欢迎\n=======\n\n"
        "即它 `链接`_ 有效。\n"
        "\n"
        ".. _链接: https://example.com\n"
    )
    html = _page(build_html(rst))
    assert "即它<a" in html
    assert ">链接</a>有效。" in html


def test_sections_admonitions_and_list_items(build_html):
    # The pass works wherever Text nodes have element siblings —
    # titles, admonition bodies, list items — not only plain paragraphs.
    rst = (
        "欢迎\n"
        "=======\n"
        "\n"
        "小节标题 *强调* 结尾\n"
        "-------------------\n"
        "\n"
        ".. note::\n"
        "\n"
        "   注意 *事项* 在此。\n"
        "\n"
        "- 列表 *项目* 内容\n"
    )
    html = _page(build_html(rst))
    assert "标题<em>强调</em>结尾" in html
    assert "注意<em>事项</em>在此。" in html
    assert "列表<em>项目</em>内容" in html


def test_escaped_space_seam_is_glued(build_html):
    # ``\ `` (an escaped space, common in translated msgstrs so translation
    # tooling cannot trim it) is stored NUL-escaped by docutils; it is just
    # as artificial a seam space and goes too.
    out = build_html("欢迎\n=======\n\n这是 *内嵌强调* \\ （注释）结尾。\n")
    html = _page(out)
    assert "这是<em>内嵌强调</em>（注释）结尾。" in html


def test_navigation_toc_uses_stripped_title(tmp_path):
    # The navigation is snapshotted by the toctree collector during
    # reading; the doctree-read pass (priority 490, before the collector's
    # 500) means the snapshot is taken from already-stripped titles.
    rst = (
        "欢迎\n=======\n\n"
        "小节 *强调* 标题\n"
        "-------------------\n\n"
        "正文。\n"
    )
    app, _out = _build(tmp_path, rst)
    toc_text = app.env.tocs["index"].astext()
    assert "小节强调标题" in toc_text
    assert "小节 强调 标题" not in toc_text
