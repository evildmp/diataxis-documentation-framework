"""Regression test: the embedded Skia font subset must retain the variation
axis tuples that the diagram actually uses.

The diagram's text styling lives in a ``<style>`` block inside the SVG
template (``extensions/diataxis_diagram/diataxis-diagram-template.svg``),
which sets ``font-variation-settings`` on three CSS classes applied to
<text> nodes:

    .axis        wght 1.3,  wdth 1.0
    .type        wght 0.6,  wdth 1.0
    .purpose     wght 1.3,  wdth 1.0

Only the ``wght`` axis is exercised away from its default (1.0); ``wdth`` is
always 1.0. If the embedded subset is ever rebuilt in a way that drops the
``wght`` axis or its end tuples (light 0.48, bold 3.2), the diagram's
``.type`` (0.6) and ``.axis`` (1.3) weights would silently clamp to the
default and the typography would regress. This test parses the SVG
template's ``font-variation-settings`` declarations and asserts the
embedded font's ``fvar``/``gvar`` can actually deliver them.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


REPO_ROOT = Path(__file__).resolve().parents[3]
STATIC_DIR = REPO_ROOT / "_static"
FONT_CSS_PATH = STATIC_DIR / "skia-font.css"
FONT_WOFF2_PATH = STATIC_DIR / "skia-subset.woff2"
SVG_TEMPLATE_PATH = (
    REPO_ROOT
    / "extensions"
    / "diataxis_diagram"
    / "diataxis-diagram-template.svg"
)


def _load_embedded_font() -> TTFont:
    assert FONT_WOFF2_PATH.is_file(), f"missing {FONT_WOFF2_PATH}"
    return TTFont(str(FONT_WOFF2_PATH))


# (axis_tag, value) pairs the diagram requests, parsed from the SVG
# template's <style> block. ``wdth`` is always 1.0 so it is not asserted
# here — the point of this test is to catch a rebuild that drops a *used*
# axis end.
def _diagram_variation_settings() -> set[tuple[str, float]]:
    svg = SVG_TEMPLATE_PATH.read_text(encoding="utf-8")
    out: set[tuple[str, float]] = set()
    for m in re.finditer(r'font-variation-settings:\s*([^;}]+)', svg):
        for tag, val in re.findall(r'"(\w{4})"\s*([0-9.]+)', m.group(1)):
            out.add((tag, float(val)))
    return out


def test_diagram_variation_settings_found():
    """Sanity check: the SVG template still declares font-variation-settings
    we can parse. If the diagram CSS is refactored to drop them, this test
    (and the ones below) need revisiting rather than silently passing."""
    settings = _diagram_variation_settings()
    assert settings, (
        f"no font-variation-settings parsed from {SVG_TEMPLATE_PATH}; "
        "has the diagram CSS stopped using variable-font axes?"
    )


def test_wght_axis_present():
    """The diagram varies weight, so the embedded font must keep the wght axis."""
    font = _load_embedded_font()
    fvar = font["fvar"]
    tags = {a.axisTag for a in fvar.axes}
    assert "wght" in tags, (
        f"embedded font has no wght axis (axes: {sorted(tags)}); "
        "the diagram sets font-variation-settings \"wght\" ..."
    )


def test_wght_axis_range_covers_svg():
    """Every wght value the SVG requests must lie within the embedded font's
    wght range. A subset that clipped the axis ends would fail here."""
    font = _load_embedded_font()
    wght_axis = next(a for a in font["fvar"].axes if a.axisTag == "wght")
    lo, hi = wght_axis.minValue, wght_axis.maxValue
    requested = {v for tag, v in _diagram_variation_settings() if tag == "wght"}
    out_of_range = sorted(v for v in requested if not (lo <= v <= hi))
    assert not out_of_range, (
        f"SVG requests wght values {out_of_range} outside the embedded "
        f"font's wght range [{lo}, {hi}]"
    )


@pytest.mark.parametrize("wght", [0.6, 1.3])
def test_wght_end_tuples_present(wght):
    """The two non-default weights the diagram uses (0.6 for .type,
    1.3 for .axis) must be reachable from the gvar tuples.

    We instance the font at the requested weight and compare a glyph's
    outline to the default instance. If the gvar tuples for that end of
    the axis were stripped, instancing at the end value would produce the
    same outline as the default — i.e. the variation is silently gone.
    """
    font = _load_embedded_font()
    default = _load_embedded_font()

    inst = instantiateVariableFont(font, {"wght": wght})

    glyf = inst["glyf"]
    default_glyf = default["glyf"]
    # 'A' is a basic glyph present in any subset that covers Latin.
    glyph_name = inst.getBestCmap()[ord("A")]

    a_inst = glyf[glyph_name]
    a_default = default_glyf[glyph_name]

    # Compare the raw coordinate arrays. A missing gvar tuple for the
    # requested end of the axis means instancing produces the default
    # outline, so the arrays would be identical.
    inst_coords = list(a_inst.coordinates) if a_inst.numberOfContours != 0 else []
    default_coords = list(a_default.coordinates) if a_default.numberOfContours != 0 else []

    assert inst_coords != default_coords, (
        f"instancing wght={wght} produces the same 'A' outline as the "
        f"default (wght=1.0); the gvar tuple for that end of the axis "
        f"is missing from the embedded subset"
    )
