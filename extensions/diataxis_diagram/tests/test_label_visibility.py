"""Per-variant label slot visibility and alt-swap class wiring.

The diagram gates each label slot on **two** conditions: the relevant
quadrant must be selected, AND the label (default or ``-alt``) must be
supplied in the content block (see ``show_*`` flags in
``on_html_visit_diataxis_diagram``). A label in a non-selected quadrant
must not render, and a missing label must not render an empty slot.

When a label has both a default and an ``-alt`` value, the default ``<span>``
gains the ``label-swappable`` class and the ``-alt`` renders as a sibling
``<span class="... label-alt">``. When only the ``-alt`` is supplied (no
default), the slot still renders with just the ``label-alt`` span — the
``show_*`` flag keys on "default OR alt".

These tests pin both behaviours so a future refactor can't silently drop a
slot or break the swap wiring.
"""

from __future__ import annotations

import importlib.util as _il
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


def _rst(args: str, labels: dict) -> str:
    lines = [f"..  diataxis-diagram:: {args}".rstrip(),
             f"   :title: {TITLE_TEXT}", f"   :desc: {DESC_TEXT}", ""]
    for name, value in labels.items():
        lines.append(f'   :{name}: "{value}"')
    return "Welcome\n=======\n\n" + "\n".join(lines) + "\n"


def _build(tmp_path: Path, args: str, labels: dict) -> str:
    out = _build_html(tmp_path, _rst(args, labels))
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    assert len(blocks) == 1, f"expected one diagram, got {len(blocks)}"
    return blocks[0]


def _has_slot(block: str, slot_class: str) -> bool:
    return f'class="slot {slot_class}"' in block or f'class="slot need {slot_class}"' in block \
        or f'class="slot type {slot_class}"' in block or f'class="slot purpose {slot_class}"' in block


# All labels supplied; the variant decides which render.
_ALL_LABELS = {
    "name-top-left": "Tutorials", "name-top-right": "How-to guides",
    "name-bottom-right": "Reference", "name-bottom-left": "Explanation",
    "purpose-top-left": "Learning", "purpose-top-right": "Problem",
    "purpose-bottom-right": "Information", "purpose-bottom-left": "Understanding",
    "axis-label-top": "Practical", "axis-label-bottom": "Conceptual",
    "axis-label-left": "Development", "axis-label-right": "Application",
    "need-top-left": "need TL", "need-top-right": "need TR",
    "need-bottom-right": "need BR", "need-bottom-left": "need BL",
}


# --- Per-quadrant visibility -------------------------------------------

def test_full_diagram_renders_all_slots(tmp_path: Path):
    block = _build(tmp_path, "", _ALL_LABELS)
    for slot in ["type-top-left", "type-top-right", "type-bottom-left", "type-bottom-right",
                 "purpose-top-left", "purpose-top-right", "purpose-bottom-left", "purpose-bottom-right",
                 "axis-label-top", "axis-label-bottom", "axis-label-left", "axis-label-right",
                 "need-top-left", "need-top-right", "need-bottom-left", "need-bottom-right"]:
        assert _has_slot(block, slot), f"missing slot {slot}:\n{block[:400]}"


def test_top_left_only_renders_only_top_left_slots(tmp_path: Path):
    block = _build(tmp_path, "top-left", _ALL_LABELS)
    # These slots belong to the top-left quadrant and its edges.
    for slot in ["type-top-left", "purpose-top-left", "need-top-left",
                 "axis-label-top", "axis-label-left"]:
        assert _has_slot(block, slot), f"missing expected slot {slot}:\n{block[:400]}"
    # These slots belong to other quadrants — must NOT render.
    for slot in ["type-top-right", "type-bottom-left", "type-bottom-right",
                 "purpose-top-right", "purpose-bottom-left", "purpose-bottom-right",
                 "need-top-right", "need-bottom-left", "need-bottom-right"]:
        assert not _has_slot(block, slot), f"unexpected slot {slot} rendered"


def test_top_right_only_renders_only_top_right_slots(tmp_path: Path):
    block = _build(tmp_path, "top-right", _ALL_LABELS)
    for slot in ["type-top-right", "purpose-top-right", "need-top-right",
                 "axis-label-top", "axis-label-right"]:
        assert _has_slot(block, slot), f"missing expected slot {slot}"
    for slot in ["type-top-left", "type-bottom-left", "type-bottom-right",
                 "purpose-top-left", "need-top-left", "need-bottom-right",
                 "axis-label-bottom"]:
        assert not _has_slot(block, slot), f"unexpected slot {slot} rendered"


def test_bottom_left_only_renders_only_bottom_left_slots(tmp_path: Path):
    block = _build(tmp_path, "bottom-left", _ALL_LABELS)
    for slot in ["type-bottom-left", "purpose-bottom-left", "need-bottom-left",
                 "axis-label-bottom", "axis-label-left"]:
        assert _has_slot(block, slot), f"missing expected slot {slot}"
    for slot in ["type-top-left", "type-bottom-right", "need-top-left",
                 "axis-label-top", "axis-label-right"]:
        assert not _has_slot(block, slot), f"unexpected slot {slot} rendered"


def test_bottom_right_only_renders_only_bottom_right_slots(tmp_path: Path):
    block = _build(tmp_path, "bottom-right", _ALL_LABELS)
    for slot in ["type-bottom-right", "purpose-bottom-right", "need-bottom-right",
                 "axis-label-bottom", "axis-label-right"]:
        assert _has_slot(block, slot), f"missing expected slot {slot}"
    for slot in ["type-top-right", "type-bottom-left", "need-top-right",
                 "axis-label-top", "axis-label-left"]:
        assert not _has_slot(block, slot), f"unexpected slot {slot} rendered"


# --- Missing labels don't render empty slots ---------------------------

def test_missing_label_omits_slot(tmp_path: Path):
    # Supply only the top-left type label; the other type slots must not
    # render, even though their quadrants are selected (full diagram).
    labels = {"name-top-left": "Tutorials"}
    block = _build(tmp_path, "", labels)
    assert _has_slot(block, "type-top-left"), block
    for slot in ["type-top-right", "type-bottom-left", "type-bottom-right",
                 "purpose-top-left", "axis-label-top", "need-top-left"]:
        assert not _has_slot(block, slot), f"unexpected slot {slot} for missing label"


# --- Alt-swap wiring ----------------------------------------------------

def test_alt_label_renders_label_swappable_and_label_alt(tmp_path: Path):
    labels = {"name-top-left": "Default", "name-top-left-alt": "Alt"}
    block = _build(tmp_path, "", labels)
    # The default span gets the label-swappable class; the alt span gets
    # label-alt. Both are <span class="type ...">.
    assert '<span class="type label-swappable">' in block, block
    assert '<span class="type label-alt">' in block, block
    assert ">Default<" in block, block
    assert ">Alt<" in block, block


def test_alt_only_still_renders_slot_with_label_alt(tmp_path: Path):
    # Only the -alt variant supplied: the slot still renders (show_* keys on
    # "default OR alt"), but there is no label-swappable default span — only
    # the label-alt span.
    labels = {"name-top-left-alt": "Alt only"}
    block = _build(tmp_path, "", labels)
    assert _has_slot(block, "type-top-left"), block
    assert '<span class="type label-alt">' in block, block
    assert ">Alt only<" in block, block
    # No default span with label-swappable (the string may appear in the
    # <style> block as a selector, so check the actual span tag).
    assert '<span class="type label-swappable">' not in block, block


def test_default_only_renders_without_swap_classes(tmp_path: Path):
    labels = {"name-top-left": "Default only"}
    block = _build(tmp_path, "", labels)
    assert _has_slot(block, "type-top-left"), block
    # The default span has class "type" only (no label-swappable; no -alt
    # supplied). The strings may appear in the <style> block as selectors,
    # so assert on the actual span tag.
    assert '<span class="type">Default only</span>' in block, block
    assert '<span class="type label-swappable">' not in block, block
    assert '<span class="type label-alt">' not in block, block
