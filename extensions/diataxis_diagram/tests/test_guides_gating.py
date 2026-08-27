"""Construction guide lines are gated by ``guides.show`` in the typography.

The template emits eight ``<div class="guide-line ...">`` elements (a frame
border on all four edges + an inner cross at the purpose-label edges) only
when the resolved ``guides`` config sets ``show: True``. The default is
``{"show": False, "x": 154, "y": 120}`` (see ``DEFAULT_TYPOGRAPHY``), so
guides are off unless a locale or the ``default`` key turns them on.

These tests pin that the eight divs appear when ``show`` is true and none
appear when it is false, so the gating can't be accidentally inverted or
dropped.
"""

from __future__ import annotations

import importlib.util as _il
from pathlib import Path

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

_GUIDE_CLASSES = [
    "guide-top", "guide-right", "guide-bottom", "guide-left",
    "guide-v-left", "guide-v-right", "guide-h-top", "guide-h-bottom",
]


def _rst() -> str:
    return (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        '   :name-top-left: "T"\n'
    )


def _block(html: str) -> str:
    blocks = _diagram_blocks(html)
    assert len(blocks) == 1, f"expected one diagram, got {len(blocks)}"
    return blocks[0]


def test_guides_absent_by_default(tmp_path: Path):
    out = _build_html(tmp_path, _rst())  # default typography: guides off
    block = _block((out / "index.html").read_text(encoding="utf-8"))
    for cls in _GUIDE_CLASSES:
        assert f'<div class="guide-line {cls}"></div>' not in block, \
            f"guide {cls} rendered when guides are off:\n{block[:400]}"


def test_guides_present_when_show_true(tmp_path: Path):
    typography = {
        "default": {"guides": {"show": True, "x": 154, "y": 120}},
        "en": {"font-sizes": {"type": 104, "purpose": 44, "axis": 44},
               "offsets": {"axis-y": 119}},
    }
    out = _build_html(tmp_path, _rst(), typography=typography)
    block = _block((out / "index.html").read_text(encoding="utf-8"))
    for cls in _GUIDE_CLASSES:
        assert f'<div class="guide-line {cls}"></div>' in block, \
            f"guide {cls} missing when guides are on:\n{block[:400]}"


def test_guides_absent_when_show_false_explicit(tmp_path: Path):
    typography = {
        "default": {"guides": {"show": False, "x": 154, "y": 120}},
        "en": {"font-sizes": {"type": 104, "purpose": 44, "axis": 44},
               "offsets": {"axis-y": 119}},
    }
    out = _build_html(tmp_path, _rst(), typography=typography)
    block = _block((out / "index.html").read_text(encoding="utf-8"))
    for cls in _GUIDE_CLASSES:
        assert f'<div class="guide-line {cls}"></div>' not in block, \
            f"guide {cls} rendered when show=False:\n{block[:400]}"


def test_guide_positions_use_configured_offsets(tmp_path: Path):
    # The inner cross sits at +/-x and +/-y from the axis. Pin that the
    # vertical guides carry distinct positions (not all the same), and that
    # they're emitted as percentages.
    typography = {
        "default": {"guides": {"show": True, "x": 200, "y": 150}},
        "en": {"font-sizes": {"type": 104, "purpose": 44, "axis": 44},
               "offsets": {"axis-y": 119}},
    }
    out = _build_html(tmp_path, _rst(), typography=typography)
    block = _block((out / "index.html").read_text(encoding="utf-8"))
    import re
    # --guide-v-left and --guide-v-right are percentages of the width.
    m_left = re.search(r"--guide-v-left:\s*([\d.]+)%", block)
    m_right = re.search(r"--guide-v-right:\s*([\d.]+)%", block)
    assert m_left and m_right, block
    assert m_left.group(1) != m_right.group(1), \
        f"vertical guides coincide: {m_left.group(1)} == {m_right.group(1)}"
