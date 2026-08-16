"""Test the ``type-x-correction`` offset.

The four type labels (Tutorials / Explanation / How-to guides / Reference) are
inset from the nominal type/purpose edge towards the origin by
``type-x-correction``, so their larger glyphs don't overflow the frame. The
purpose labels and guide lines stay at the nominal ``type-purpose-x`` edge.

This test pins that the correction moves only the type labels, inwards on both
sides, and leaves the purpose labels and guides untouched.
"""

from __future__ import annotations

import importlib.util as _il
import re
from pathlib import Path

from sphinx.application import Sphinx

# Load the shared fixtures from the sibling conftest.py by path.
_spec = _il.spec_from_file_location(
    "_diataxis_diagram_conftest",
    Path(__file__).resolve().parent / "conftest.py",
)
assert _spec is not None and _spec.loader is not None
_mod = _il.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LABEL_VALUES = _mod.LABEL_VALUES
TITLE_TEXT = _mod.TITLE_TEXT
DESC_TEXT = _mod.DESC_TEXT
_ensure_extensions_importable = _mod._ensure_extensions_importable


_CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Diátaxis"
language = {language!r}
master_doc = "index"
exclude_patterns = []
diataxis_diagram = {typography!r}
"""


def _index_rst() -> str:
    label_lines = "\n   ".join(
        f':{name}: "{value}"' for name, value in LABEL_VALUES.items()
    )
    return (
        "Welcome\n"
        "=======\n"
        "\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f"   {label_lines}"
    )


def _build(tmp_path: Path, typography: dict) -> Path:
    _ensure_extensions_importable()
    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"

    src.mkdir(parents=True)
    (src / "conf.py").write_text(
        _CONF_PY.format(language="en", typography=typography),
        encoding="utf-8",
    )
    (src / "index.rst").write_text(_index_rst(), encoding="utf-8")

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(doctree),
        buildername="html",
        freshenv=True,
    )
    app.build()
    return out


def _inlined_svg(html: str) -> str:
    m = re.search(r'(<svg[^>]*>.*?</svg>)', html, re.DOTALL)
    assert m is not None, "no <svg> block found in HTML"
    return m.group(1)


def _x_attr(svg: str, label_id: str) -> int:
    """Return the integer x attribute of the <text id=label_id> element."""
    m = re.search(
        r'<text[^>]*\bid="' + re.escape(label_id) + r'"[^>]*\bx="(-?\d+)"',
        svg,
    )
    assert m is not None, f'no <text id="{label_id}"> with an x attribute in SVG'
    return int(m.group(1))


_BASE_TYPOGRAPHY = {
    "en": {
        "font-sizes": {"type": 104, "purpose": 44, "axis": 44},
        "offsets": {
            "axis-x": 154,
            "type-purpose-x": 154,
            "axis-y": 119,
            "purpose-y": 119,
            "type-y": 240,
        },
        "y-axis-rotation": "rotated",
        "guides": True,
    },
}


def _typography_with_correction(correction: int | None) -> dict:
    import copy

    typo = copy.deepcopy(_BASE_TYPOGRAPHY)
    if correction is not None:
        typo["en"]["offsets"]["type-x-correction"] = correction
    return typo


# The four type labels that must move with the correction.
TYPE_LABELS_LEFT = ("tutorials", "explanation")
TYPE_LABELS_RIGHT = ("how-to", "reference")
# Purpose labels must stay at the nominal edge.
PURPOSE_LABELS_LEFT = ("orientation-tutorial", "orientation-explanation")
PURPOSE_LABELS_RIGHT = ("orientation-how-to", "orientation-reference")


def test_no_correction_keeps_type_labels_at_nominal_edge(tmp_path: Path):
    """With no ``type-x-correction`` set, the type labels sit at the same x
    as the purpose labels (the nominal ``type-purpose-x`` edge)."""
    out = _build(tmp_path, _typography_with_correction(None))
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))

    nominal = 154
    for name in TYPE_LABELS_LEFT + PURPOSE_LABELS_LEFT:
        assert _x_attr(svg, name) == -nominal, (name, _x_attr(svg, name))
    for name in TYPE_LABELS_RIGHT + PURPOSE_LABELS_RIGHT:
        assert _x_attr(svg, name) == nominal, (name, _x_attr(svg, name))


def test_correction_moves_type_labels_inwards(tmp_path: Path):
    """A correction of 5 moves each type label 5 units towards the origin:
    right-side labels shrink by 5, left-side labels grow by 5 (towards 0)."""
    out = _build(tmp_path, _typography_with_correction(5))
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))

    expected = 154 - 5  # 149
    for name in TYPE_LABELS_RIGHT:
        assert _x_attr(svg, name) == expected, (name, _x_attr(svg, name))
    for name in TYPE_LABELS_LEFT:
        assert _x_attr(svg, name) == -expected, (name, _x_attr(svg, name))


def test_correction_leaves_purpose_labels_untouched(tmp_path: Path):
    """The correction must not move the purpose labels; they stay at the
    nominal ``type-purpose-x`` edge."""
    out = _build(tmp_path, _typography_with_correction(5))
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))

    nominal = 154
    for name in PURPOSE_LABELS_LEFT:
        assert _x_attr(svg, name) == -nominal, (name, _x_attr(svg, name))
    for name in PURPOSE_LABELS_RIGHT:
        assert _x_attr(svg, name) == nominal, (name, _x_attr(svg, name))


def test_correction_leaves_guides_untouched(tmp_path: Path):
    """The vertical guide lines stay at the nominal edge; only the type
    labels move."""
    out = _build(tmp_path, _typography_with_correction(5))
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))

    # The two vertical guides at ±type-purpose-x (154).
    assert 'x1="-154"' in svg and 'x2="-154"' in svg, svg
    assert 'x1="154"' in svg and 'x2="154"' in svg, svg
    # The inset edge (149) must not appear on any guide line.
    assert 'x1="-149"' not in svg
    assert 'x1="149"' not in svg


def test_correction_falls_back_to_default_zero(tmp_path: Path):
    """When the locale omits ``type-x-correction``, the built-in default of 0
    applies: type labels are not inset."""
    out = _build(tmp_path, _typography_with_correction(None))
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))

    # No 149 edge should exist; type labels are at 154.
    assert 'x="-149"' not in svg
    assert 'x="149"' not in svg


def test_correction_zero_explicit_matches_omitted(tmp_path: Path):
    """An explicit correction of 0 matches the omitted (default) case."""
    out = _build(tmp_path, _typography_with_correction(0))
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))

    for name in TYPE_LABELS_LEFT:
        assert _x_attr(svg, name) == -154, (name, _x_attr(svg, name))
    for name in TYPE_LABELS_RIGHT:
        assert _x_attr(svg, name) == 154, (name, _x_attr(svg, name))


def test_no_placeholder_survives(tmp_path: Path):
    """The new ``{{ type_x }}`` variable must resolve; no ``{{``/``}}`` may
    survive in the inlined SVG."""
    out = _build(tmp_path, _typography_with_correction(5))
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))
    assert "{{" not in svg, f"unsubstituted placeholder in SVG:\n{svg}"
    assert "}}" not in svg, f"unsubstituted placeholder in SVG:\n{svg}"
