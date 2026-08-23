"""Tests for :left-half: / :right-half: annotation labels and
:x-axis: / :y-axis: directive args.

Scope (approved by user):

* :left-half: / :right-half: — multiline annotation labels anchored at 25 % /
  75 % across the visible region and vertically centered, mirroring
  :top-half: / :bottom-half: which anchor at 25 % / 75 % down and are
  horizontally centered. Each line of a multiline label is stored as its own
  translatable inline node and re-collected at render time; per-line
  translatability is already covered by the 12-label gettext tests (same
  ``_make_label_node`` path), so these tests focus on rendering geometry.

* :x-axis: / :y-axis: — directive positional args that independently gate the
  horizontal / vertical axis lines. Previously only :axes: existed, which
  enables both; these two allow each axis to be controlled separately.
"""

from __future__ import annotations

import importlib.util as _il
import re
from pathlib import Path

import pytest
from sphinx.application import Sphinx

# Load shared fixtures from the sibling conftest.py by path (pattern copied
# from test_placeholder_substitution.py — avoids mutating the shared conftest,
# whose EXPECTED_MSGIDS count of 14 is asserted elsewhere).
_spec = _il.spec_from_file_location(
    "_diataxis_diagram_conftest_labels",
    Path(__file__).resolve().parent / "conftest.py",
)
assert _spec is not None and _spec.loader is not None
_mod = _il.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TITLE_TEXT = _mod.TITLE_TEXT
DESC_TEXT = _mod.DESC_TEXT
_ensure_extensions_importable = _mod._ensure_extensions_importable

# Axis font size used by the test typography (matches DEFAULT_TYPOGRAPHY).
# pad = 2 * 42 = 84 in _quadrant_bounds for the quadrant-subset test.
_AXIS_FONT_SIZE = 42

# Canvas geometry (mirrors _FULL_* in the extension source).
_FULL_LEFT, _FULL_RIGHT = -960, 960
_FULL_TOP, _FULL_BOTTOM = -540, 540


_CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Daniele Procida"
language = {language!r}
master_doc = "index"
exclude_patterns = []
diataxis_diagram = {{
    "en": {{"font-sizes": {{"axis": 42}}}},
}}
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _index_rst(directive_args="", labels=()):
    """Build a minimal index.rst with a diataxis-diagram directive.

    ``directive_args`` is the positional argument string (e.g. ``"x-axis"``,
    ``"top-left"``, or ``""`` for none). ``labels`` is a sequence of
    ``(name, value)`` pairs; for multiline labels, use per-part quoting
    (``'"L1", "L2"'``), matching the convention in
    ``source/snippets/diagram-top-bottom.rst``.
    """
    header = "..  diataxis-diagram::"
    if directive_args:
        header += " " + directive_args
    lines = [
        "Welcome",
        "=======",
        "",
        header,
        f"   :title: {TITLE_TEXT}",
        f"   :desc: {DESC_TEXT}",
    ]
    if labels:
        lines.append("")  # blank line: options → content block
        for name, value in labels:
            lines.append(f"   :{name}: {value}")
    return "\n".join(lines) + "\n"


def _build_svg(tmp_path, directive_args="", labels=()):
    """Build a Sphinx project (real, un-monkeypatched template) and return
    the inlined SVG string."""
    _ensure_extensions_importable()
    rst = _index_rst(directive_args, labels)

    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"
    src.mkdir()
    (src / "conf.py").write_text(
        _CONF_PY.format(language="en"), encoding="utf-8"
    )
    (src / "index.rst").write_text(rst, encoding="utf-8")

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(doctree),
        buildername="html",
        freshenv=True,
    )
    app.build()
    html = (out / "index.html").read_text(encoding="utf-8")
    m = re.search(r"(<svg[^>]*>.*?</svg>)", html, re.DOTALL)
    assert m is not None, "no <svg> block found in HTML"
    return m.group(1)


def _annotation_group(svg, group_id):
    """Return the ``<g id="group_id" ...>...</g>`` string, or ``''``."""
    pattern = rf'<g\b[^>]*\bid="{re.escape(group_id)}"[^>]*>.*?</g>'
    m = re.search(pattern, svg, re.DOTALL)
    return m.group(0) if m else ""


def _translate(element):
    """Parse ``transform="translate(X Y)"`` on *element* -> ``(x, y)`` floats,
    or ``(None, None)`` if absent."""
    m = re.search(r'\btransform="translate\(([^)]*)\)"', element)
    if not m:
        return None, None
    parts = m.group(1).split()
    if len(parts) != 2:
        return None, None
    return float(parts[0]), float(parts[1])


def _line_texts(element):
    """Return list of text contents of all ``<text>`` children in element."""
    return re.findall(r"<text\b[^>]*>(.*?)</text>", element, re.DOTALL)


def _axis_lines(svg):
    """Return list of attribute dicts for ``<line>`` elements with
    ``stroke='black'`` (i.e. axis lines, not guides which use '#999')."""
    lines = re.findall(r"<line\b([^>]*)/>", svg)
    result = []
    for attrs_str in lines:
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', attrs_str))
        if attrs.get("stroke") == "black":
            result.append(attrs)
    return result


def _expected_anchors(v_left, v_right, v_top, v_bottom):
    """Compute expected annotation anchor values for the given visible region.

    Mirrors the formula in ``on_html_visit_diataxis_diagram``.
    """
    return {
        "left_x": v_left + (v_right - v_left) / 4,
        "right_x": v_left + 3 * (v_right - v_left) / 4,
        "center_y": (v_top + v_bottom) / 2,
    }


# ---------------------------------------------------------------------------
# :left-half: / :right-half: tests
# ---------------------------------------------------------------------------


def test_left_half_renders_with_correct_anchor(tmp_path):
    """``:left-half:`` renders a ``<g id="annotation-left-half">`` translated
    to 25 % across the visible region and vertically centered, with one
    standalone ``<text>`` per comma-separated part."""
    svg = _build_svg(tmp_path, labels=[("left-half", '"L1", "L2"')])
    elem = _annotation_group(svg, "annotation-left-half")
    assert elem, "annotation-left-half group not found in SVG"

    anchors = _expected_anchors(_FULL_LEFT, _FULL_RIGHT, _FULL_TOP, _FULL_BOTTOM)
    tx, ty = _translate(elem)
    assert tx == pytest.approx(anchors["left_x"])
    assert ty == pytest.approx(anchors["center_y"])

    assert _line_texts(elem) == ["L1", "L2"]


def test_right_half_renders_with_correct_anchor(tmp_path):
    """``:right-half:`` renders a ``<g id="annotation-right-half">`` translated
    to 75 % across the visible region and vertically centered."""
    svg = _build_svg(tmp_path, labels=[("right-half", '"R1", "R2"')])
    elem = _annotation_group(svg, "annotation-right-half")
    assert elem, "annotation-right-half group not found in SVG"

    anchors = _expected_anchors(_FULL_LEFT, _FULL_RIGHT, _FULL_TOP, _FULL_BOTTOM)
    tx, ty = _translate(elem)
    assert tx == pytest.approx(anchors["right_x"])
    assert ty == pytest.approx(anchors["center_y"])

    assert _line_texts(elem) == ["R1", "R2"]


def test_single_line_label_renders_one_tspan(tmp_path):
    """A single-value ``:left-half:`` (no comma) produces exactly one
    standalone ``<text>``."""
    svg = _build_svg(tmp_path, labels=[("left-half", '"Only"')])
    elem = _annotation_group(svg, "annotation-left-half")
    assert elem
    assert _line_texts(elem) == ["Only"]


def test_quoted_comma_is_preserved_as_one_item(tmp_path):
    """A comma inside surrounding quotes is part of one item, not a split.

    ``:left-half: "Hello, world"`` renders a single ``<text>`` whose content
    is ``Hello, world`` — the inner comma does not create a second line.
    """
    svg = _build_svg(tmp_path, labels=[("left-half", '"Hello, world"')])
    elem = _annotation_group(svg, "annotation-left-half")
    assert elem, "annotation-left-half group not found in SVG"
    assert _line_texts(elem) == ["Hello, world"]


def test_quoted_comma_item_mixed_with_plain_item(tmp_path):
    """A quoted-comma item and a plain item yield two ``<text>`` children.

    ``:left-half: "Hello, world", "L2"`` renders two lines: ``Hello, world``
    (one item, inner comma preserved) and ``L2``.
    """
    svg = _build_svg(tmp_path, labels=[("left-half", '"Hello, world", "L2"')])
    elem = _annotation_group(svg, "annotation-left-half")
    assert elem, "annotation-left-half group not found in SVG"
    assert _line_texts(elem) == ["Hello, world", "L2"]


def test_left_right_half_absent_by_default(tmp_path):
    """No ``:left-half:`` / ``:right-half:`` in the RST produces no annotation
    groups (the template gates each on truthiness)."""
    svg = _build_svg(tmp_path)
    assert _annotation_group(svg, "annotation-left-half") == ""
    assert _annotation_group(svg, "annotation-right-half") == ""


def test_quadrant_subset_recomputes_left_half_anchor(tmp_path):
    """With a single quadrant (``top-left``), the left-half anchor recomputes
    against the subset's visible region, not the full-diagram bounds. This
    guards the ``v_left`` / ``v_right`` plumbing through ``_quadrant_bounds``."""
    svg = _build_svg(
        tmp_path,
        directive_args="top-left",
        labels=[("left-half", '"L1"')],
    )
    elem = _annotation_group(svg, "annotation-left-half")
    assert elem

    # top-left only: the region runs from the full left/top edge to a stub
    # of 2 * axis_font_size past the origin.
    pad = 2 * _AXIS_FONT_SIZE
    anchors = _expected_anchors(_FULL_LEFT, pad, _FULL_TOP, pad)

    # The anchor must differ from the full-diagram value (-480) …
    assert anchors["left_x"] != pytest.approx(-480.0)
    # … and match the subset-specific value (-699).
    tx, ty = _translate(elem)
    assert tx == pytest.approx(anchors["left_x"])
    assert ty == pytest.approx(anchors["center_y"])


# ---------------------------------------------------------------------------
# :x-axis: / :y-axis: arg tests
# ---------------------------------------------------------------------------


def test_x_axis_arg_shows_horizontal_only(tmp_path):
    """``x-axis`` positional arg shows the horizontal axis line but not the
    vertical."""
    svg = _build_svg(tmp_path, directive_args="x-axis")
    black = _axis_lines(svg)
    horizontal = [l for l in black if l.get("y1") == "0" and l.get("y2") == "0"]
    vertical = [l for l in black if l.get("x1") == "0" and l.get("x2") == "0"]
    assert len(horizontal) == 1, f"expected 1 horizontal axis line, got {horizontal}"
    assert len(vertical) == 0, f"expected 0 vertical axis lines, got {vertical}"


def test_y_axis_arg_shows_vertical_only(tmp_path):
    """``y-axis`` positional arg shows the vertical axis line but not the
    horizontal."""
    svg = _build_svg(tmp_path, directive_args="y-axis")
    black = _axis_lines(svg)
    horizontal = [l for l in black if l.get("y1") == "0" and l.get("y2") == "0"]
    vertical = [l for l in black if l.get("x1") == "0" and l.get("x2") == "0"]
    assert len(horizontal) == 0, f"expected 0 horizontal axis lines, got {horizontal}"
    assert len(vertical) == 1, f"expected 1 vertical axis line, got {vertical}"


def test_x_and_y_axis_args_show_both(tmp_path):
    """``x-axis y-axis`` (both new args together) shows both axis lines."""
    svg = _build_svg(tmp_path, directive_args="x-axis y-axis")
    black = _axis_lines(svg)
    horizontal = [l for l in black if l.get("y1") == "0" and l.get("y2") == "0"]
    vertical = [l for l in black if l.get("x1") == "0" and l.get("x2") == "0"]
    assert len(horizontal) == 1
    assert len(vertical) == 1


def test_axes_arg_shows_both(tmp_path):
    """``axes`` positional arg shows both axis lines (backward compatibility)."""
    svg = _build_svg(tmp_path, directive_args="axes")
    black = _axis_lines(svg)
    horizontal = [l for l in black if l.get("y1") == "0" and l.get("y2") == "0"]
    vertical = [l for l in black if l.get("x1") == "0" and l.get("x2") == "0"]
    assert len(horizontal) == 1
    assert len(vertical) == 1


def test_no_category_args_shows_both(tmp_path):
    """No positional args (default) shows both axis lines (backward
    compatibility — categories is None, so both show_x_axis / show_y_axis
    are True)."""
    svg = _build_svg(tmp_path)
    black = _axis_lines(svg)
    horizontal = [l for l in black if l.get("y1") == "0" and l.get("y2") == "0"]
    vertical = [l for l in black if l.get("x1") == "0" and l.get("x2") == "0"]
    assert len(horizontal) == 1
    assert len(vertical) == 1


# ---------------------------------------------------------------------------
# :need-*: / :need-*-alt: tests
# ---------------------------------------------------------------------------
#
# The ``need-*`` family mirrors the quadrant-name family (``top-left``,
# ``top-right-name``, ``bottom-right-name``, ``bottom-left-name``) in geometry
# and carries the ``.need`` class (driving the ``.need`` CSS rule and the
# ``{{ need_font_size }}`` substitution), but never a ``.type`` / ``.purpose``
# class — the family has its own typography. Each ``need-*`` may take a
# ``need-*-alt`` hover/tap alternative; alt-only groups must still render (the
# ``show_need_*`` gates use "default OR alt present").
#
# The test typography (``_CONF_PY``) sets only ``font-sizes.axis = 42``; all
# offsets come from ``DEFAULT_TYPOGRAPHY`` in ``__init__.py``: ``type-purpose-x
# = 154``, ``type-x-correction = 0`` ⇒ ``type_x = 154``; ``type-y = 240``.

_NEED_TYPE_X = 154
_NEED_TYPE_Y = 240


def _text_by_id(svg, text_id):
    """Return the ``<text id="text_id" ...>...</text>`` string, or ``''``."""
    pattern = rf'<text\b[^>]*\bid="{re.escape(text_id)}"[^>]*>.*?</text>'
    m = re.search(pattern, svg, re.DOTALL)
    return m.group(0) if m else ""


def _text_attrs(text_elem):
    """Parse attribute dict from a ``<text ...>`` opening tag."""
    m = re.match(r"<text\b([^>]*)>", text_elem)
    if not m:
        return {}
    return dict(re.findall(r'(\w[\w-]*)="([^"]*)"', m.group(1)))


@pytest.mark.parametrize(
    "name,alt_name,x_sign,y_sign,anchor",
    [
        ("need-top-left", "need-top-left-alt", -1, -1, "end"),
        ("need-bottom-left-name", "need-bottom-left-name-alt", -1, 1, "end"),
        ("need-top-right-name", "need-top-right-name-alt", 1, -1, "start"),
        ("need-bottom-right-name", "need-bottom-right-name-alt", 1, 1, "start"),
    ],
)
def test_need_alt_only_renders_at_quadrant_name_position(
    tmp_path, name, alt_name, x_sign, y_sign, anchor
):
    """With only ``:<alt_name>:`` set, the alt ``<text>`` renders at the same
    geometry as the corresponding quadrant-name label, and no default
    ``<text>`` is emitted."""
    svg = _build_svg(tmp_path, labels=[(alt_name, "alt value")])
    alt = _text_by_id(svg, alt_name)
    assert alt, f"{alt_name} <text> not found in SVG"

    attrs = _text_attrs(alt)
    assert "label-alt" in attrs.get("class", "").split()
    assert "need" in attrs.get("class", "").split()
    assert attrs.get("text-anchor") == anchor
    assert attrs.get("dominant-baseline") == "middle"
    assert attrs.get("x") == str(x_sign * _NEED_TYPE_X)
    assert attrs.get("y") == str(y_sign * _NEED_TYPE_Y)
    assert ">alt value<" in alt

    # No default <text> for this family when only the alt is supplied.
    assert _text_by_id(svg, name) == ""


@pytest.mark.parametrize(
    "name,alt_name,x_sign,y_sign,anchor",
    [
        ("need-top-left", "need-top-left-alt", -1, -1, "end"),
        ("need-bottom-left-name", "need-bottom-left-name-alt", -1, 1, "end"),
        ("need-top-right-name", "need-top-right-name-alt", 1, -1, "start"),
        ("need-bottom-right-name", "need-bottom-right-name-alt", 1, 1, "start"),
    ],
)
def test_need_default_and_alt_render_together(
    tmp_path, name, alt_name, x_sign, y_sign, anchor
):
    """When both default and alt are supplied, the default is tagged
    ``label-swappable`` (so the swap CSS can hide it on hover) and the alt is
    tagged ``label-alt``; both sit at the same coordinates."""
    svg = _build_svg(
        tmp_path,
        labels=[(name, "default value"), (alt_name, "alt value")],
    )
    default = _text_by_id(svg, name)
    alt = _text_by_id(svg, alt_name)
    assert default and alt

    default_attrs = _text_attrs(default)
    assert "label-swappable" in default_attrs.get("class", "").split()
    assert "need" in default_attrs.get("class", "").split()
    assert default_attrs.get("text-anchor") == anchor
    assert default_attrs.get("x") == str(x_sign * _NEED_TYPE_X)
    assert default_attrs.get("y") == str(y_sign * _NEED_TYPE_Y)

    alt_attrs = _text_attrs(alt)
    assert "label-alt" in alt_attrs.get("class", "").split()
    assert "need" in alt_attrs.get("class", "").split()
    assert alt_attrs.get("x") == str(x_sign * _NEED_TYPE_X)
    assert alt_attrs.get("y") == str(y_sign * _NEED_TYPE_Y)


def test_need_labels_carry_need_class(tmp_path):
    """``need-*`` ``<text>`` elements carry the ``.need`` class (driving the
    ``.need`` CSS rule and ``{{ need_font_size }}`` substitution) but never a
    ``.type`` / ``.purpose`` class — the family has its own typography."""
    svg = _build_svg(
        tmp_path,
        labels=[
            ("need-top-left", "a"),
            ("need-top-right-name", "b"),
            ("need-bottom-right-name", "c"),
            ("need-bottom-left-name", "d"),
        ],
    )
    for name in (
        "need-top-left",
        "need-top-right-name",
        "need-bottom-right-name",
        "need-bottom-left-name",
    ):
        elem = _text_by_id(svg, name)
        assert elem, f"{name} <text> not found"
        cls = _text_attrs(elem).get("class", "").split()
        assert "need" in cls
        assert "type" not in cls
        assert "purpose" not in cls


def test_need_labels_absent_by_default(tmp_path):
    """No ``:need-*:`` options in the RST ⇒ no ``need-*`` ``<text>`` elements
    are emitted (the ``show_need_*`` gates evaluate false)."""
    svg = _build_svg(tmp_path)
    for name in (
        "need-top-left",
        "need-top-left-alt",
        "need-top-right-name",
        "need-top-right-name-alt",
        "need-bottom-right-name",
        "need-bottom-right-name-alt",
        "need-bottom-left-name",
        "need-bottom-left-name-alt",
    ):
        assert _text_by_id(svg, name) == "", f"unexpected {name} <text> in SVG"


def test_need_alt_absent_when_only_default_supplied(tmp_path):
    """Supplying a default ``:need-top-left:`` without an alt emits the default
    ``<text>`` with no class (not ``label-swappable``) and no alt ``<text>``."""
    svg = _build_svg(tmp_path, labels=[("need-top-left", "only default")])
    default = _text_by_id(svg, "need-top-left")
    assert default
    assert _text_attrs(default).get("class", "").split() == ["need"]
    assert _text_by_id(svg, "need-top-left-alt") == ""


def test_need_labels_respect_quadrant_subset(tmp_path):
    """``need-*`` labels are gated on the quadrant being selected: with only
    ``top-left`` in the directive args, ``need-bottom-left-name-alt`` does not
    render even when supplied."""
    svg = _build_svg(
        tmp_path,
        directive_args="top-left",
        labels=[
            ("need-top-left-alt", "shown"),
            ("need-bottom-left-name-alt", "hidden"),
        ],
    )
    assert _text_by_id(svg, "need-top-left-alt"), "top-left alt should render"
    assert _text_by_id(svg, "need-bottom-left-name-alt") == (
        ""
    ), "bottom-left alt must not render when bottom-left quadrant is absent"
