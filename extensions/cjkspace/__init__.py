"""Sphinx extension: strip artificial spaces around inline markup in CJK text.

The problem (cf. https://github.com/tats-u/markdown-cjk-friendly)
----------------------------------------------------------------
reStructuredText — like CommonMark, cf. the ``markdown-cjk-friendly``
specification — only recognises inline markup delimiters (``*emphasis*``,
``**strong**``, literals, ...) when they are flanked by whitespace or
punctuation.  CJK characters qualify as neither, so emphasis embedded in
CJK prose has to be padded with spaces to parse at all::

    即它 *为什么* 有效

Translators add these spaces especially on translation platforms such as
Transifex, where the rendered output cannot be previewed and the markup
rules are not understood — the exact scenario ``markdown-cjk-friendly``
was written for.  The spaces then leak into the rendered page as unwanted
gaps between CJK text and the emphasised span::

    即它 <em>为什么</em> 有效

Chinese and Japanese typography put no space between characters, so the
spaces there are artefacts of the markup workaround, not of the prose.
Korean is the exception: it separates words with spaces, so the same
spaces are real and the extension leaves them alone (see below).

The fix (after https://github.com/seisman/sphinx-cjkspace)
----------------------------------------------------------
Like ``sphinx-cjkspace`` removes newline-induced spaces between CJK
characters after parsing, this extension post-processes the resolved
doctree — at ``doctree-read``, before the navigation snapshots section
titles, and again at ``doctree-resolved``, the last stage before writing
— and deletes the artificial whitespace there.  Parsing and the message
catalogs are never touched.

A whitespace run at the seam between a ``Text`` node and a neighbouring
inline element (emphasis, strong, literal, reference, ...) is dropped when
both characters flanking it belong to a script written without word
spaces:

* the last (or first) character of the ``Text`` node, and
* the first (or last) character rendered by the neighbouring element.

That is not "CJK" as a whole.  Chinese and Japanese run their characters
together, so a space around markup there is an artefact of the parsing
workaround; Korean separates words with spaces, so the same space is a
real word boundary and must stay.  Hangul is therefore excluded.  The
unspaced set is Han (Chinese and Japanese kanji), hiragana, katakana,
bopomofo and the punctuation those scripts share (。、「」——……“”), and it
is spelled out as Unicode blocks below so a reader can check exactly what
qualifies.  Latin, wide emoji and other scripts do not qualify, which also
keeps the (desirable) space between CJK and Latin text, and leaves prose
in other languages untouched.

Newline-wrapped source counts as whitespace too, so markup at the start
of a continuation line is glued as well, mirroring sphinx-cjkspace's line
joining.

The ``gettext`` builder is skipped, so ``.pot`` msgids stay verbatim for
translators; ``literal_block`` (which includes parsed literals) and
``math_block`` are skipped because whitespace there is significant.
"""

from __future__ import annotations

import re

from docutils import nodes

__version__ = "0.1.0"

# Unicode blocks of scripts written without spaces between characters.
# Hangul is deliberately absent: Korean separates words with spaces, so a
# space next to Hangul is a real word boundary and must be kept. A missing
# block here can only leave a space in place — never remove a needed one.
_UNSPACED_BLOCKS = (
    (0x2E80, 0x2EFF),    # CJK Radicals Supplement
    (0x2F00, 0x2FDF),    # Kangxi Radicals
    (0x2FF0, 0x2FFF),    # Ideographic Description Characters
    (0x3000, 0x303F),    # CJK Symbols and Punctuation
    (0x3040, 0x309F),    # Hiragana
    (0x30A0, 0x30FF),    # Katakana
    (0x3100, 0x312F),    # Bopomofo
    (0x3190, 0x31BF),    # Kanbun, Bopomofo Extended
    (0x31C0, 0x31EF),    # CJK Strokes
    (0x31F0, 0x31FF),    # Katakana Phonetic Extensions
    (0x3400, 0x4DBF),    # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),    # CJK Unified Ideographs
    (0xF900, 0xFAFF),    # CJK Compatibility Ideographs
    (0xFE10, 0xFE1F),    # Vertical Forms
    (0xFE30, 0xFE4F),    # CJK Compatibility Forms
    (0xFE50, 0xFE6F),    # Small Form Variants
    (0xFF01, 0xFF60),    # Fullwidth Forms
    (0xFF61, 0xFF9F),    # Halfwidth CJK punctuation and katakana
    (0xFFE0, 0xFFE6),    # Fullwidth Signs
    (0x1B000, 0x1B16F),  # Kana Supplement, Kana Extended-A, Small Kana Ext.
    (0x20000, 0x2FA1F),  # CJK Extensions B-F, Compatibility Supplement
    (0x30000, 0x323AF),  # CJK Extensions G-H
)

# Punctuation shared by those scripts but living outside the blocks above:
# ambiguous-width dashes, ellipses and quotation marks.
_UNSPACED_PUNCTUATION = frozenset("—–―…‥“”‘’·")

# Whitespace runs at a Text node's seams. \s matches the fullwidth space
# U+3000 as well as newlines, so a source line wrapped right before
# markup joins too. The optional \x00 is docutils' escape marker: an
# escaped space (``\ ``, common in translated msgstrs so tooling keeps
# it) is stored as NUL + space and is just as artificial a seam space.
_LEADING_WS = re.compile(r"^(?:\x00?\s)+")
_TRAILING_WS = re.compile(r"(?:\x00?\s)+$")

# Parents whose children are left alone: whitespace is significant in
# literal blocks (``.. parsed-literal::`` shares the literal_block class)
# and in math.
_PRESERVE_PARENTS = (nodes.literal_block, nodes.math_block)


def is_unspaced_char(char: str) -> bool:
    """True if *char* belongs to a script written without word spaces.

    Han (Chinese and Japanese kanji), hiragana, katakana, bopomofo and the
    punctuation those scripts share qualify. Hangul does not — Korean
    separates words with spaces — and neither do Latin, emoji or other
    scripts.

    >>> is_unspaced_char("中") or is_unspaced_char("あ") or is_unspaced_char("。")
    True
    >>> is_unspaced_char("한") or is_unspaced_char("A") or is_unspaced_char("😀")
    False
    """
    if not char or char.isspace():
        return False
    if char in _UNSPACED_PUNCTUATION:
        return True
    codepoint = ord(char)
    return any(start <= codepoint <= end for start, end in _UNSPACED_BLOCKS)


def _edge_char(node: nodes.Element, *, last: bool) -> str:
    """First (or last) character that *node* renders.

    ``""`` when the node renders nothing visible (an image without alt
    text, an inline target), which keeps the neighbouring space.
    """
    text = node.astext()
    return text[-1:] if last else text[:1]


def _replace_text(parent: nodes.Element, index: int, raw: str) -> bool:
    """Swap the Text node at ``parent.children[index]`` for one holding *raw*.

    docutils Text nodes are ``str`` subclasses with no mutable data slot,
    so the node has to be replaced rather than edited. ``setup_child``
    keeps the parent/document pointers intact, and assignment is by index
    so identical-content siblings elsewhere in the same parent cannot be
    confused (``index()`` would match them via str equality).
    """
    fresh = nodes.Text(raw)
    parent.setup_child(fresh)
    parent.children[index] = fresh
    return True


def _strip_trailing(parent: nodes.Element, index: int) -> bool:
    """Drop Text node *index*'s trailing whitespace run.

    Fires when the character before the run in the Text node and the
    first character of the element following it are both unspaced.
    """
    raw = str(parent.children[index])
    match = _TRAILING_WS.search(raw)
    if match is None or match.start() == 0:
        # no run, or the node is all whitespace (a middle case handled
        # by _strip_inner_space)
        return False
    if not (
        is_unspaced_char(raw[match.start() - 1])
        and is_unspaced_char(_edge_char(parent.children[index + 1], last=False))
    ):
        return False
    return _replace_text(parent, index, raw[: match.start()])


def _strip_leading(parent: nodes.Element, index: int) -> bool:
    """Drop Text node *index*'s leading whitespace run.

    Fires when the character after the run in the Text node and the last
    character of the element preceding it are both unspaced.
    """
    raw = str(parent.children[index])
    match = _LEADING_WS.match(raw)
    if match is None or match.end() == len(raw):
        return False
    rest = raw[match.end() :]
    if not (
        is_unspaced_char(rest[0])
        and is_unspaced_char(_edge_char(parent.children[index - 1], last=True))
    ):
        return False
    return _replace_text(parent, index, rest)


def _strip_inner_space(parent: nodes.Element) -> None:
    """Blank a whitespace-only Text node caught between two elements.

    ``*甲* *乙*`` needs the middle space to parse, yet renders as
    ``甲乙``: the space is artificial too. Only fires when both elements
    render unspaced text at the seam.
    """
    children = parent.children
    for i in range(1, len(children) - 1):
        node = children[i]
        if not isinstance(node, nodes.Text) or str(node).replace("\x00", "").strip():
            continue
        left, right = children[i - 1], children[i + 1]
        if isinstance(left, nodes.Text) or isinstance(right, nodes.Text):
            continue
        left_unspaced = is_unspaced_char(_edge_char(left, last=True))
        right_unspaced = is_unspaced_char(_edge_char(right, last=False))
        if left_unspaced and right_unspaced:
            _replace_text(parent, i, "")


def fix_inline_boundaries(parent: nodes.Element) -> None:
    """Strip artificial unspaced-script boundary spaces among children.

    Only seams between a Text node and a neighbouring element are
    considered; Text↔Text siblings (which do not occur in parsed
    docutils trees) are left alone. Parents where whitespace is
    significant are skipped.
    """
    if isinstance(parent, _PRESERVE_PARENTS):
        return
    children = parent.children
    for i in range(len(children) - 1):
        left, right = children[i], children[i + 1]
        if isinstance(left, nodes.Text):
            if not isinstance(right, nodes.Text):
                _strip_trailing(parent, i)
        elif isinstance(right, nodes.Text):
            _strip_leading(parent, i + 1)
    _strip_inner_space(parent)


def process_cjk_boundaries(app, doctree, docname=None):
    """Strip artificial unspaced-script boundary spaces from a tree.

    Connected to two events:

    ``doctree-read`` (priority 490, before the toctree collector's 500)
    so the section titles snapshotted for the navigation are already
    stripped, and ``doctree-resolved`` — the last stage before writing —
    so the page itself is final too. Translations are in place by then:
    the ``Locale`` transform re-parses every msgstr during reading, and
    both passes are idempotent.

    The ``gettext`` builder is skipped: message extraction reads
    ``rawsource`` (which this pass never touches), so there is nothing to
    gain there.
    """
    if app.builder.name == "gettext":
        return
    for parent in list(doctree.findall(nodes.Element)):
        fix_inline_boundaries(parent)


def setup(app):
    # Before the toctree collector snapshots section titles for the
    # navigation (it connects to doctree-read at the default priority).
    app.connect("doctree-read", process_cjk_boundaries, priority=490)
    app.connect("doctree-resolved", process_cjk_boundaries)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
