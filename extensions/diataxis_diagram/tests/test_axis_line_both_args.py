"""The ``-both`` suffix on directive args renders axis lines always visible.

The positional directive args (``x-axis`` / ``y-axis`` / ``axes``) gate the
axis-line ``<div>``s. Each may carry an ``-alt`` suffix (hover-revealed; see
``test_axis_line_alt_args``) or a ``-both`` suffix (always visible, plain — no
swap classes). The suffix is stripped to get the base arg (which still drives
quadrant selection and visibility); the ``-both`` flag renders a plain axis
line that never fades.

Semantics (mirroring the ``-alt`` family, confirmed by the user):

* ``x-axis-both``: the x-axis line, always visible (plain, no swap classes).
  No advert cue — ``-both`` signals no hover interaction.
* ``axes-both``: both axis lines, always visible (plain).
* ``-both`` is accepted on any arg syntactically, but only ``x-axis`` /
  ``y-axis`` / ``axes`` gate an axis-line element, so ``-both`` on a quadrant
  or no-op category arg is a no-op (the base arg applies normally).
* ``-both`` does NOT wire a swap and does NOT fire the advert cue.
* ``x-axis-both y-axis-alt``: x-both is plain (always visible, never fades);
  y-alt is ``label-alt`` (hidden unhovered, shown on hover). The advert cue
  fires (because ``y-axis-alt`` is an ``-alt``); x-both stays visible on hover.

These tests pin the rendered axis-line structure for each combination so the
``-both`` wiring can't silently regress.
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


# The exact axis-line tags the template emits.
# default / swappable default / alt / both (both is plain, like default but
# never swappable — distinguished from the no-suffix default by the absence of
# a matching default arg; here we only assert on the both variant's plainness).
X_DEFAULT = '<div class="axis-line x-axis"></div>'
X_SWAPPABLE = '<div class="axis-line x-axis label-swappable"></div>'
X_ALT = '<div class="axis-line x-axis label-alt"></div>'
Y_DEFAULT = '<div class="axis-line y-axis"></div>'
Y_SWAPPABLE = '<div class="axis-line y-axis label-swappable"></div>'
Y_ALT = '<div class="axis-line y-axis label-alt"></div>'
ADVERT = '<div class="advert-cue">'


# --- -both renders a plain axis line, no swap, no cue -------------------

@pytest.mark.parametrize("args", ["x-axis-both", "y-axis-both", "axes-both"])
def test_both_arg_renders_plain_axis_line_no_swap_no_cue(tmp_path: Path, args: str):
    body = _body(_build(tmp_path, args))
    if "x-axis" in args or "axes" in args:
        assert X_DEFAULT in body, f"{args}: x-axis plain line missing"
    if "y-axis" in args or "axes" in args:
        assert Y_DEFAULT in body, f"{args}: y-axis plain line missing"
    assert X_SWAPPABLE not in body, f"{args}: x-axis swapped (should be plain -both)"
    assert Y_SWAPPABLE not in body, f"{args}: y-axis swapped (should be plain -both)"
    assert X_ALT not in body and Y_ALT not in body, f"{args}: alt lines present for -both"
    assert ADVERT not in body, f"{args}: advert cue rendered for -both (should be absent)"


def test_x_axis_both_renders_only_x_plain(tmp_path: Path):
    body = _body(_build(tmp_path, "x-axis-both"))
    assert X_DEFAULT in body, "x-axis plain line missing"
    assert Y_DEFAULT not in body, "y-axis line present for x-axis-both"
    assert X_SWAPPABLE not in body, "x-axis swapped for x-axis-both"
    assert ADVERT not in body, "advert cue for x-axis-both"


def test_y_axis_both_renders_only_y_plain(tmp_path: Path):
    body = _body(_build(tmp_path, "y-axis-both"))
    assert Y_DEFAULT in body, "y-axis plain line missing"
    assert X_DEFAULT not in body, "x-axis line present for y-axis-both"
    assert Y_SWAPPABLE not in body, "y-axis swapped for y-axis-both"
    assert ADVERT not in body, "advert cue for y-axis-both"


def test_axes_both_renders_both_plain_no_cue(tmp_path: Path):
    body = _body(_build(tmp_path, "axes-both"))
    assert X_DEFAULT in body, "x-axis plain line missing for axes-both"
    assert Y_DEFAULT in body, "y-axis plain line missing for axes-both"
    assert X_SWAPPABLE not in body and Y_SWAPPABLE not in body, "axes-both lines swapped"
    assert ADVERT not in body, "advert cue rendered for axes-both"


# --- -both + -alt: both stays plain, alt swaps, cue fires ---------------

def test_x_axis_both_y_axis_alt_x_stays_plain_y_alt_swaps(tmp_path: Path):
    # x-axis-both is plain (always visible, never fades); y-axis-alt is
    # label-alt (hidden unhovered, shown on hover). The advert cue fires
    # because y-axis-alt is an -alt. x-axis-both must NOT gain label-swappable
    # (it stays visible on hover).
    body = _body(_build(tmp_path, "x-axis-both y-axis-alt"))
    assert X_DEFAULT in body, "x-axis-both plain line missing"
    assert X_SWAPPABLE not in body, "x-axis-both gained label-swappable (should stay plain)"
    assert Y_ALT in body, "y-axis-alt line missing"
    assert Y_DEFAULT not in body and Y_SWAPPABLE not in body, "y-axis default present (should be alt-only)"
    assert ADVERT in body, "advert cue missing with y-axis-alt present"


def test_x_axis_alt_y_axis_both_x_alt_swaps_y_stays_plain(tmp_path: Path):
    body = _body(_build(tmp_path, "x-axis-alt y-axis-both"))
    assert X_ALT in body, "x-axis-alt line missing"
    assert Y_DEFAULT in body, "y-axis-both plain line missing"
    assert Y_SWAPPABLE not in body, "y-axis-both gained label-swappable"
    assert X_DEFAULT not in body, "x-axis default present (should be alt-only)"
    assert ADVERT in body, "advert cue missing with x-axis-alt present"


# --- -both on a quadrant arg is a no-op (base arg applies) -------------

def test_quadrant_arg_both_is_noop_for_axis_lines(tmp_path: Path):
    # top-left-both is accepted (stripped to top-left, which selects that
    # quadrant) but does NOT wire an axis-line swap or fire the advert cue —
    # the base arg applies normally. With no axis-related arg, no axis lines
    # are drawn at all. Only assert on swap/alt/cue, not on the default lines
    # (which are absent: no axis args were supplied).
    body = _body(_build(tmp_path, "top-left-both"))
    assert X_SWAPPABLE not in body, "quadrant -both wired an axis swap"
    assert Y_SWAPPABLE not in body, "quadrant -both wired an axis swap"
    assert X_ALT not in body and Y_ALT not in body, "quadrant -both rendered an alt axis line"
    assert ADVERT not in body, "quadrant -both fired the advert cue"


# --- -both does NOT fire the advert cue (only -alt does) -----------------

def test_both_only_does_not_fire_advert(tmp_path: Path):
    body = _body(_build(tmp_path, "axes-both"))
    assert ADVERT not in body, "axes-both fired the advert cue"


def test_both_with_alt_fires_advert(tmp_path: Path):
    body = _body(_build(tmp_path, "axes-both x-axis-alt"))
    assert ADVERT in body, "advert cue missing with x-axis-alt present alongside -both"
