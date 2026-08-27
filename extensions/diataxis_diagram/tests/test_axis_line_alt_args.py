"""The ``-alt`` suffix on directive args swaps axis lines on hover.

The positional directive args (``x-axis`` / ``y-axis`` / ``axes``) gate the
axis-line ``<div>``s. Each may carry an ``-alt`` suffix marking it as the
hover-revealed variant, mirroring the ``-alt`` label properties (see
``test_interactive_swap`` and ``test_label_visibility``). The suffix is
stripped to get the base arg (which still drives quadrant selection and
visibility); the ``-alt`` flag is tracked so the axis line swaps.

Semantics (confirmed by the user):

* ``x-axis`` (no ``-alt``): the default axis line, visible unhovered. When any
  axis-line ``-alt`` arg is present anywhere in the directive, the default line
  gains ``label-swappable`` and fades out on hover (so the alt lines take its
  place).
* ``x-axis-alt``: the alt axis line, rendered with ``label-alt`` (hidden
  unhovered, revealed on hover).
* ``x-axis y-axis-alt``: unhovered → only x visible; hovered → only y visible
  (x swaps out, y-alt swaps in).
* ``y-axis y-axis-alt``: the line is always visible (the default swaps out,
  the alt swaps in; net always shown).
* ``axes-alt``: both axis lines as ``label-alt`` (hidden unhovered, shown on
  hover).
* ``-alt`` is accepted on any arg syntactically, but only ``x-axis`` / ``y-axis``
  / ``axes`` gate a swappable element (an axis line). A ``-alt`` on a quadrant
  arg (e.g. ``top-left-alt``) or a no-op category arg (``axis-labels-alt`` /
  ``type-alt`` / ``purpose-alt``) is a no-op — the base arg applies normally
  and no swap is wired.

The advert cue (see ``test_advert_cue``) also fires when any axis-line ``-alt``
arg is present (in addition to the existing label-alt trigger), since the cue
signals "this diagram has a hover interaction".

These tests pin the rendered axis-line structure for each combination so the
swap wiring can't silently regress.
"""

from __future__ import annotations

import importlib.util as _il
import re
from pathlib import Path

import pytest

_spec = _il.spec_from_file_location(
    "_diataxis_diagram_conftest",
    Path(__file__).resolve().parent / "conftest.py",
)
assert _spec is not None and _spec.loader is not None
_mod = _il.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_build_html = _mod._build_html
_diagram_blocks = _mod._diagram_blocks
TITLE_TEXT = _mod.TITLE_TEXT
DESC_TEXT = _mod.DESC_TEXT


def _rst(args: str) -> str:
    lines = [f"..  diataxis-diagram:: {args}".rstrip(),
             f"   :title: {TITLE_TEXT}", f"   :desc: {DESC_TEXT}", ""]
    return "Welcome\n=======\n\n" + "\n".join(lines) + "\n"


def _block(html: str) -> str:
    blocks = _diagram_blocks(html)
    assert len(blocks) == 1, f"expected one diagram, got {len(blocks)}"
    return blocks[0]


def _build(tmp_path: Path, args: str) -> str:
    out = _build_html(tmp_path, _rst(args))
    return _block((out / "index.html").read_text(encoding="utf-8"))


def _body(block: str) -> str:
    """The block with its ``<style>`` stripped, so substring assertions hit
    real tags rather than CSS selectors that mention the same class names."""
    return re.sub(r"<style>.*?</style>", "", block, flags=re.DOTALL)


# The exact axis-line tags the template emits (default, swappable default, alt).
X_DEFAULT = '<div class="axis-line x-axis"></div>'
X_SWAPPABLE = '<div class="axis-line x-axis label-swappable"></div>'
X_ALT = '<div class="axis-line x-axis label-alt"></div>'
Y_DEFAULT = '<div class="axis-line y-axis"></div>'
Y_SWAPPABLE = '<div class="axis-line y-axis label-swappable"></div>'
Y_ALT = '<div class="axis-line y-axis label-alt"></div>'
ADVERT = '<div class="advert-cue">'


# --- No axis args: no axis lines, no swap, no cue -----------------------

def test_no_args_renders_no_axes_no_swap_no_cue(tmp_path: Path):
    body = _body(_build(tmp_path, ""))
    assert X_DEFAULT not in body, "x-axis default line rendered with no axis args"
    assert Y_DEFAULT not in body, "y-axis default line rendered with no axis args"
    assert X_SWAPPABLE not in body, "x-axis swapped with no alt present"
    assert Y_SWAPPABLE not in body, "y-axis swapped with no alt present"
    assert X_ALT not in body and Y_ALT not in body, "alt axis lines with no alt arg"
    assert ADVERT not in body, "advert cue rendered with no alt"


@pytest.mark.parametrize("args", ["x-axis", "y-axis", "axes"])
def test_default_axis_arg_no_alt_no_swap_no_cue(tmp_path: Path, args: str):
    body = _body(_build(tmp_path, args))
    assert X_SWAPPABLE not in body, f"{args}: x-axis swapped with no alt"
    assert Y_SWAPPABLE not in body, f"{args}: y-axis swapped with no alt"
    assert X_ALT not in body and Y_ALT not in body, f"{args}: alt line with no alt arg"
    assert ADVERT not in body, f"{args}: advert cue rendered with no alt"


# --- The user's headline case: x-axis y-axis-alt ------------------------

def test_x_axis_y_axis_alt_shows_x_unhovered_y_hovered(tmp_path: Path):
    # Unhovered: only x visible (default, swappable). Hovered: x fades out,
    # y fades in (alt). So: x default present + swappable, y default absent,
    # y-alt present, advert cue present.
    body = _body(_build(tmp_path, "x-axis y-axis-alt"))
    assert X_SWAPPABLE in body, "x-axis default line is not swappable"
    assert X_DEFAULT not in body, "x-axis default line missing label-swappable"
    assert Y_ALT in body, "y-axis alt line missing"
    assert Y_DEFAULT not in body and Y_SWAPPABLE not in body, "y-axis default present (should be alt-only)"
    assert ADVERT in body, "advert cue missing with axis-line -alt present"


# --- y-axis y-axis-alt: line always visible -----------------------------

def test_y_axis_y_axis_alt_line_always_visible(tmp_path: Path):
    # Both the default (swappable) and the alt (label-alt) y-axis line render:
    # the default covers the unhovered state, the alt covers the hovered state.
    body = _body(_build(tmp_path, "y-axis y-axis-alt"))
    assert Y_SWAPPABLE in body, "y-axis default line is not swappable"
    assert Y_ALT in body, "y-axis alt line missing"
    assert ADVERT in body, "advert cue missing"


def test_x_axis_x_axis_alt_line_always_visible(tmp_path: Path):
    body = _body(_build(tmp_path, "x-axis x-axis-alt"))
    assert X_SWAPPABLE in body, "x-axis default line is not swappable"
    assert X_ALT in body, "x-axis alt line missing"
    assert ADVERT in body, "advert cue missing"


# --- Alt-only: line hidden unhovered, shown on hover --------------------

@pytest.mark.parametrize("args,x_alt,y_alt", [
    ("x-axis-alt", X_ALT, None),
    ("y-axis-alt", None, Y_ALT),
    ("axes-alt", X_ALT, Y_ALT),
])
def test_alt_only_renders_label_alt_no_default(
    tmp_path: Path, args: str, x_alt: str, y_alt: str
):
    body = _body(_build(tmp_path, args))
    assert X_DEFAULT not in body, f"{args}: default x-axis present (should be alt-only)"
    assert Y_DEFAULT not in body, f"{args}: default y-axis present (should be alt-only)"
    assert X_SWAPPABLE not in body, f"{args}: swappable x-axis present (should be alt-only)"
    assert Y_SWAPPABLE not in body, f"{args}: swappable y-axis present (should be alt-only)"
    if x_alt is not None:
        assert x_alt in body, f"{args}: {x_alt} missing"
    if y_alt is not None:
        assert y_alt in body, f"{args}: {y_alt} missing"
    assert ADVERT in body, f"{args}: advert cue missing with axis-line -alt present"


def test_axes_alt_renders_both_alt_no_default(tmp_path: Path):
    body = _body(_build(tmp_path, "axes-alt"))
    assert X_ALT in body, "x-axis alt line missing for axes-alt"
    assert Y_ALT in body, "y-axis alt line missing for axes-alt"
    assert X_DEFAULT not in body and Y_DEFAULT not in body, "default axis lines present for axes-alt"
    assert ADVERT in body, "advert cue missing for axes-alt"


# --- -alt on non-axis args is a no-op (no swap, no cue) -----------------

def test_quadrant_arg_alt_is_noop_for_axis_lines(tmp_path: Path):
    # top-left-alt is accepted (stripped to top-left, which selects that
    # quadrant) but does NOT wire an axis-line swap or fire the advert cue,
    # because quadrant args gate geometry, not a swappable element.
    body = _body(_build(tmp_path, "top-left-alt"))
    assert X_SWAPPABLE not in body, "quadrant -alt wired an axis swap"
    assert Y_SWAPPABLE not in body, "quadrant -alt wired an axis swap"
    assert X_ALT not in body and Y_ALT not in body, "quadrant -alt rendered an alt axis line"
    assert ADVERT not in body, "quadrant -alt fired the advert cue"


def test_x_axis_with_quadrant_alt_no_axis_swap(tmp_path: Path):
    # x-axis (default, no swap) + top-left-alt (quadrant, no-op for lines).
    # The x-axis line is present but NOT swappable; no advert cue.
    body = _body(_build(tmp_path, "x-axis top-left-alt"))
    assert X_DEFAULT in body, "x-axis default line missing"
    assert X_SWAPPABLE not in body, "quadrant -alt wired an axis swap on x-axis"
    assert X_ALT not in body, "x-axis alt line present with no x-axis-alt arg"
    assert ADVERT not in body, "advert cue fired with no axis-line -alt"


# --- Advert cue fires on axis-line -alt, not on quadrant -alt -----------

def test_advert_cue_present_for_axis_line_alt(tmp_path: Path):
    body = _body(_build(tmp_path, "x-axis-alt"))
    assert ADVERT in body, "advert cue missing for x-axis-alt"


def test_advert_cue_absent_for_quadrant_alt_only(tmp_path: Path):
    body = _body(_build(tmp_path, "top-left-alt"))
    assert ADVERT not in body, "advert cue fired for a quadrant -alt only"
