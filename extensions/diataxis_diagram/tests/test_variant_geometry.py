"""Geometry of the HTML/CSS diagram across quadrant subsets.

``.. diataxis-diagram::`` accepts an optional positional argument naming the
quadrants to show (one of ``top-left`` / ``top-right`` / ``bottom-left`` /
``bottom-right``, or a union). The extension computes the grid tracks, axis
position, aspect ratio and flip flags in ``_html_geometry`` and emits them as
CSS custom properties on the diagram's inner ``<div>`` and as classes
(``diagram--<variant>``, ``diagram--axis-high`` / ``diagram--axis-low``).

These tests pin the structural shape of that output per variant so a future
change to ``_html_geometry`` can't silently move an axis or flip a label
direction. Exact percentages are asserted only for the full diagram (where
the geometry is symmetric and stable); subset variants are pinned by the
sign of their offsets (axis above/below 50 %, left/right of 50 %) and by
the variant class and flip flag, which is what the layout's correctness
actually depends on.
"""

from __future__ import annotations

import importlib.util as _il
import re
from pathlib import Path

import pytest

# Path-load the shared conftest helpers (see test_diataxis_diagram_font_sizes
# for the rationale — tests don't share a package root, so they reach the
# sibling conftest by file path rather than importing it).
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


def _diagram(rst_args: str = "", *, labels: dict | None = None) -> str:
    """An ``index.rst`` invoking the directive with given args and labels.

    Labels live in the directive's content block (body lines), not in its
    option spec (which is only ``title`` / ``desc`` / ``class``), so a blank
    line separates the options from the ``:label: value`` body lines.
    """
    lines = [f"..  diataxis-diagram:: {rst_args}".rstrip()]
    lines.append(f"   :title: {TITLE_TEXT}")
    lines.append(f"   :desc: {DESC_TEXT}")
    lines.append("")  # blank line ends the option block; body follows
    if labels:
        for name, value in labels.items():
            lines.append(f'   :{name}: "{value}"')
    return "Welcome\n=======\n\n" + "\n".join(lines) + "\n"


# A minimal label set that satisfies the template's visibility flags for all
# four quadrants, so subset variants still render their slots.
_ALL_LABELS = {
    "name-top-left": "Tutorials",
    "name-top-right": "How-to guides",
    "name-bottom-right": "Reference",
    "name-bottom-left": "Explanation",
}


def _build_variant(tmp_path: Path, rst_args: str, typography=None) -> str:
    out = _build_html(tmp_path, _diagram(rst_args, labels=_ALL_LABELS),
                      typography=typography)
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    assert len(blocks) == 1, f"expected one diagram, got {len(blocks)}"
    return blocks[0]


def _inner_div_class(block: str) -> str:
    """The ``class`` attribute of the diagram's inner ``<div id=...>``.

    The outer div carries the user-facing ``diataxis-diagram`` class; the
    inner div carries the variant / y-axis-mode / axis-flip classes. The
    flip classes also appear as CSS selectors in the scoped ``<style>`` block,
    so a substring search of the whole block can't tell applied classes from
    selectors — extract the attribute instead.
    """
    m = re.search(r'<div id="[^"]+"\s+class="([^"]+)"', block)
    assert m, f"no inner div with class found in block:\n{block[:200]}"
    return m.group(1)


# --- Full diagram -------------------------------------------------------

def test_full_diagram_variant_class(tmp_path: Path):
    block = _build_variant(tmp_path, "")
    cls = _inner_div_class(block)
    assert "diagram--full" in cls.split(), cls


def test_full_diagram_geometry_is_symmetric(tmp_path: Path):
    block = _build_variant(tmp_path, "")
    cls = _inner_div_class(block)
    # Both axes cross at the centre of the full diagram.
    assert re.search(r"--axis-x-pos:\s*50\.0000%", block), block
    assert re.search(r"--axis-y-pos:\s*50\.0000%", block), block
    # Two equal columns (1fr 1fr); three rows for top quad / axis band /
    # bottom quad.
    assert "--grid-cols: 1fr 1fr" in block, block
    assert "--grid-rows:" in block and block.count("%") >= 3, block
    # 16:9 aspect ratio (1920×1080 canvas reduced by gcd 120).
    assert "--aspect-ratio: 16 / 9" in block, block
    # Central row is the middle of three.
    assert "--central-row: 2" in block, block
    # No flip flag on the symmetric full diagram (the axis sits at 50 %).
    assert "diagram--axis-high" not in cls, cls
    assert "diagram--axis-low" not in cls, cls


def test_full_diagram_y_axis_mode_default_is_rotated(tmp_path: Path):
    block = _build_variant(tmp_path, "")
    cls = _inner_div_class(block)
    assert "diagram--rotated" in cls, cls
    assert "diagram--stacked" not in cls, cls


def test_y_axis_mode_stacked_from_config(tmp_path: Path):
    typography = {
        "default": {"y-axis-rotation": "stacked"},
        "en": {"font-sizes": {"type": 104, "purpose": 44, "axis": 44},
               "offsets": {"axis-y": 119}},
    }
    block = _build_variant(tmp_path, "", typography=typography)
    cls = _inner_div_class(block)
    assert "diagram--stacked" in cls, cls
    assert "diagram--rotated" not in cls, cls


# --- Single-quadrant variants ------------------------------------------

@pytest.mark.parametrize(
    "args,variant,flip",
    [
        ("top-left",     "diagram--top-left",     "diagram--axis-high"),
        ("top-right",    "diagram--top-right",    "diagram--axis-high"),
        ("bottom-left",  "diagram--bottom-left",  "diagram--axis-low"),
        ("bottom-right", "diagram--bottom-right", "diagram--axis-low"),
    ],
)
def test_single_quadrant_variant_class_and_flip(
    tmp_path: Path, args: str, variant: str, flip: str
):
    block = _build_variant(tmp_path, args)
    cls = _inner_div_class(block)
    assert variant in cls, cls
    assert flip in cls, cls
    other_flip = "diagram--axis-low" if flip == "diagram--axis-high" else "diagram--axis-high"
    assert other_flip not in cls, cls


@pytest.mark.parametrize(
    "args,x_sign,y_sign",
    [
        ("top-left",     ">", ">"),  # axis right of centre, below centre
        ("top-right",    "<", ">"),
        ("bottom-left",  ">", "<"),
        ("bottom-right", "<", "<"),
    ],
)
def test_single_quadrant_axis_offsets_from_centre(
    tmp_path: Path, args: str, x_sign: str, y_sign: str
):
    """The axis cross sits at the inner corner of the visible quadrant, so
    for a single-quadrant view the axis is offset from 50 % toward that
    corner. This pins the sign of the offset (the structural invariant); the
    exact magnitude depends on the stub size and isn't asserted here."""
    block = _build_variant(tmp_path, args)
    m_x = re.search(r"--axis-x-pos:\s*([\d.]+)%", block)
    m_y = re.search(r"--axis-y-pos:\s*([\d.]+)%", block)
    assert m_x and m_y, block
    x = float(m_x.group(1))
    y = float(m_y.group(1))
    assert eval(f"{x} {x_sign} 50"), f"axis-x {x} expected {x_sign} 50"
    assert eval(f"{y} {y_sign} 50"), f"axis-y {y} expected {y_sign} 50"
    # Subset variants use explicit percentage columns (a stub column appears).
    assert "--grid-cols:" in block and "1fr 1fr" not in block, block


# --- Half variants -----------------------------------------------------

@pytest.mark.parametrize(
    "args,variant",
    [
        ("top-left top-right",   "diagram--top"),
        ("bottom-left bottom-right", "diagram--bottom"),
        ("top-left bottom-left", "diagram--left"),
        ("top-right bottom-right", "diagram--right"),
    ],
)
def test_half_variant_class(tmp_path: Path, args: str, variant: str):
    block = _build_variant(tmp_path, args)
    cls = _inner_div_class(block)
    # Exact-token check: `diagram--top` must not match `diagram--top-left`.
    tokens = cls.split()
    assert variant in tokens, (cls, tokens)


def test_top_half_is_axis_high(tmp_path: Path):
    block = _build_variant(tmp_path, "top-left top-right")
    cls = _inner_div_class(block)
    assert "diagram--axis-high" in cls, cls
    assert "diagram--axis-low" not in cls, cls


def test_bottom_half_is_axis_low(tmp_path: Path):
    block = _build_variant(tmp_path, "bottom-left bottom-right")
    cls = _inner_div_class(block)
    assert "diagram--axis-low" in cls, cls
    assert "diagram--axis-high" not in cls, cls


# --- Axis lines ---------------------------------------------------------

def test_no_args_renders_no_axes(tmp_path: Path):
    block = _build_variant(tmp_path, "")
    assert '<div class="axis-line x-axis"></div>' not in block, block
    assert '<div class="axis-line y-axis"></div>' not in block, block


def test_x_axis_arg_renders_only_x(tmp_path: Path):
    block = _build_variant(tmp_path, "x-axis")
    assert '<div class="axis-line x-axis"></div>' in block, block
    assert '<div class="axis-line y-axis"></div>' not in block, block


def test_y_axis_arg_renders_only_y(tmp_path: Path):
    block = _build_variant(tmp_path, "y-axis")
    assert '<div class="axis-line y-axis"></div>' in block, block
    assert '<div class="axis-line x-axis"></div>' not in block, block
