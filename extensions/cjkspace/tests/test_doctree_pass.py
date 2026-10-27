"""Unit tests for the doctree pass itself (no Sphinx build).

Pins the contract of ``fix_inline_boundaries``: seams glue, non-CJK seams
stay, parent pointers survive the Text replacement, and the pass is
idempotent (``doctree-resolved`` may fire more than once per document).
"""

from __future__ import annotations

from docutils import nodes

from extensions.cjkspace import fix_inline_boundaries


def _paragraph(*parts) -> nodes.paragraph:
    para = nodes.paragraph()
    for part in parts:
        para += part
    return para


def test_both_seams_glue():
    para = _paragraph(
        nodes.Text("即它 "),
        nodes.emphasis("为什么", "为什么"),
        nodes.Text(" 有效。"),
    )

    fix_inline_boundaries(para)

    assert para.astext() == "即它为什么有效。"
    assert [child.astext() for child in para.children] == ["即它", "为什么", "有效。"]
    # Replaced Text nodes keep their parent pointer.
    assert all(child.parent is para for child in para.children)


def test_non_cjk_seams_are_kept():
    para = _paragraph(
        nodes.Text("中文 "),
        nodes.emphasis("English", "English"),
        nodes.Text(" 中文。"),
    )

    fix_inline_boundaries(para)

    assert para.astext() == "中文 English 中文。"


def test_literal_block_parent_is_skipped():
    block = nodes.literal_block()
    block += nodes.Text("即它 ")
    block += nodes.emphasis("为什么", "为什么")

    fix_inline_boundaries(block)

    assert block.astext() == "即它 为什么"


def test_whitespace_only_text_between_elements():
    para = _paragraph(
        nodes.strong("甲", "甲"),
        nodes.Text(" "),
        nodes.strong("乙", "乙"),
    )

    fix_inline_boundaries(para)

    assert str(para[1]) == ""
    assert para.astext() == "甲乙"


def test_idempotent():
    para = _paragraph(
        nodes.Text("即它 "),
        nodes.emphasis("为什么", "为什么"),
        nodes.Text(" 有效。"),
    )

    fix_inline_boundaries(para)
    first = para.astext()
    fix_inline_boundaries(para)

    assert para.astext() == first == "即它为什么有效。"


def test_no_trailing_run_is_a_noop():
    para = _paragraph(nodes.Text("即它"), nodes.emphasis("为什么", "为什么"))

    fix_inline_boundaries(para)

    assert para.astext() == "即它为什么"
    assert str(para[0]) == "即它"
