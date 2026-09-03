"""The advert cue appears iff the hover state is enabled (any ``-alt``).

The pulsing three-dots cue in the diagram's corner is a discoverability hint
that an interactive swap is available. The template gates it on
``show_advert`` (``on_html_visit_diataxis_diagram``): true iff any ``-alt``
is present anywhere — a label name ending in ``-alt``, a non-empty
half-annotation ``-alt`` list, an axis-line ``-alt`` arg, or
``blur-alt``/``collapse-alt``. ``-both`` never fires it. The cue's
``@keyframes`` name is shared (one global ``diataxis-diagram-cue-pulse`` in
the extension's stylesheet); the pulse never varies per instance.

These tests pin:

* the cue is absent when no ``-alt`` is supplied;
* the cue is present (with its ring + pulse + three dots) when any
  ``-alt`` label is supplied;
* the ``@keyframes`` name is the single shared
  ``diataxis-diagram-cue-pulse``;
* the cue stays visible on ``:hover`` / ``:focus-visible`` — it hides only
  on ``:focus`` inside the touch-only ``@media (hover: none)`` block (see
  ``test_hover_state_semantics``).
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
shared_css = _mod.shared_css
TITLE_TEXT = _mod.TITLE_TEXT
DESC_TEXT = _mod.DESC_TEXT


def _rst(labels: dict) -> str:
    lines = [f"..  diataxis-diagram::",
             f"   :title: {TITLE_TEXT}", f"   :desc: {DESC_TEXT}", ""]
    for name, value in labels.items():
        lines.append(f'   :{name}: "{value}"')
    return "Welcome\n=======\n\n" + "\n".join(lines) + "\n"


def _block(html: str) -> str:
    blocks = _diagram_blocks(html)
    assert len(blocks) == 1, f"expected one diagram, got {len(blocks)}"
    return blocks[0]


def _build_block(tmp_path: Path, labels: dict) -> str:
    out = _build_html(tmp_path, _rst(labels))
    return _block((out / "index.html").read_text(encoding="utf-8"))


def _diagram_id(block: str) -> str:
    m = re.search(r'<div id="(diataxis-diagram-\d+)"', block)
    assert m, f"no diagram id found:\n{block[:200]}"
    return m.group(1)


# --- Presence / absence ------------------------------------------------

def test_cue_absent_when_no_alt_labels(tmp_path: Path):
    block = _build_block(tmp_path, {"name-top-left": "Default"})
    # Check for the actual cue div tag, not the CSS selectors (which always
    # appear in the scoped <style> block).
    assert '<div class="advert-cue">' not in block, \
        "advert cue rendered when no -alt labels supplied"


@pytest.mark.parametrize(
    "alt_label",
    [
        "name-top-left-alt",
        "name-top-right-alt",
        "name-bottom-right-alt",
        "name-bottom-left-alt",
        "purpose-top-left-alt",
        "purpose-top-right-alt",
        "purpose-bottom-right-alt",
        "purpose-bottom-left-alt",
        "axis-label-top-alt",
        "axis-label-bottom-alt",
        "axis-label-left-alt",
        "axis-label-right-alt",
    ],
)
def test_cue_present_when_any_quadrant_alt_label(tmp_path: Path, alt_label: str):
    # Supply the -alt variant alongside its default (so the slot renders).
    default = alt_label.removesuffix("-alt")
    block = _build_block(tmp_path, {default: "D", alt_label: "A"})
    assert '<div class="advert-cue">' in block, \
        f"advert cue absent when {alt_label} supplied:\n{block[:400]}"


def test_cue_present_when_half_annotation_alt(tmp_path: Path):
    # The half-annotation -alt lists also trigger show_advert.
    block = _build_block(tmp_path, {"top-half-alt": "Alt half"})
    assert '<div class="advert-cue">' in block, block


# --- Cue structure ------------------------------------------------------

def test_cue_has_ring_pulse_and_three_dots(tmp_path: Path):
    block = _build_block(tmp_path, {"name-top-left": "D", "name-top-left-alt": "A"})
    assert '<div class="cue-ring"></div>' in block, block
    assert '<div class="cue-pulse">' in block, block
    # Three white dots inside the pulse.
    assert block.count('<i></i>') >= 3, block


# --- Keyframes namespacing ---------------------------------------------

def test_keyframes_name_is_shared():
    css = shared_css()
    assert "@keyframes diataxis-diagram-cue-pulse" in css, \
        "no shared @keyframes diataxis-diagram-cue-pulse"


def test_pulse_animation_references_shared_keyframes():
    css = shared_css()
    assert "animation: diataxis-diagram-cue-pulse" in css, css


def test_keyframes_is_50_50_on_off():
    css = shared_css()
    # Opacity 1 -> 0 -> 1 over 2s ease-in-out infinite.
    m = re.search(r"@keyframes\s+diataxis-diagram-cue-pulse", css)
    assert m, f"no @keyframes cue-pulse found:\n{css[:600]}"
    after = css[m.start():]
    assert "opacity: 1" in after and "opacity: 0" in after, \
        f"keyframes body missing opacity 1/0:\n{after[:300]}"


# --- Stays visible on hover/focus ---------------------------------------

def test_cue_stays_visible_on_hover_and_focus(tmp_path: Path):
    block = _build_block(tmp_path, {"name-top-left": "D", "name-top-left-alt": "A"})
    did = _diagram_id(block)
    # The cue must NOT be hidden on hover/focus-visible — it stays on at all times.
    assert not re.search(rf"#{re.escape(did)}:hover\s+\.advert-cue", block), block
    assert not re.search(rf"#{re.escape(did)}:focus-visible\s+\.advert-cue", block), block
