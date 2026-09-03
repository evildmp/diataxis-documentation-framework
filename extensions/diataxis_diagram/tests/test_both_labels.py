"""The ``-both`` suffix on label options + global label swap.

The ``-both`` suffix on label options (``:name-top-left-both:``, ``:axis-label-top-both:``,
``:top-half-both:``, etc.) renders a label that is **always visible** — no swap
classes, no fade on hover. It completes the triad:

* no suffix  — default state (unhovered); fades out on hover when any ``-alt``
  label is present anywhere in the diagram (global swap).
* ``-alt``   — hover-revealed state; hidden unhovered, shown on hover.
* ``-both``  — always visible; plain, never swappable.

The label swap is **global**: any ``-alt`` anywhere (label, half-annotation,
axis-line arg, ``blur``/``collapse``) enables the hover state and makes ALL
default (no-suffix) elements ``label-swappable`` (fade out on hover) — strict
fade-out, even with no ``-alt`` replacement. ``-both`` labels are never
swappable and never enable the state.

These tests pin:

* ``-both`` labels render plain (no ``label-swappable`` / ``label-alt``);
* ``-both`` labels are always visible (no advert cue from ``-both`` alone —
  the cue fires on ``-alt``, not ``-both``);
* the global label swap: a default label with no own ``-alt`` still gains
  ``label-swappable`` when a different label's ``-alt`` is present;
* ``-both`` labels stay visible even when ``label_swap_active`` is true
  (another label's ``-alt`` is present);
* the combination of all three (default + alt + both) renders all three
  spans with the right classes.
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


ADVERT = '<div class="advert-cue">'


# --- -both renders plain (no swap classes) ------------------------------

def test_both_label_renders_plain_no_swap_classes(tmp_path: Path):
    block = _build(tmp_path, "", {"name-top-left-both": "Both"})
    # The -both span renders as a plain <span class="type"> (no label-swappable,
    # no label-alt). The string "label-swappable" may appear in the <style>
    # block as a selector, so assert on the actual span tag.
    assert '<span class="type">Both</span>' in block, block
    assert 'Both' in block, block


def test_both_label_renders_without_label_swappable(tmp_path: Path):
    block = _build(tmp_path, "", {"name-top-left-both": "Both"})
    assert '<span class="type label-swappable">' not in block, \
        "label-swappable applied to a -both-only label"
    assert '<span class="type label-alt">' not in block, \
        "label-alt applied to a -both-only label"


def test_both_only_does_not_fire_advert(tmp_path: Path):
    # -both signals no hover interaction; the advert cue fires on -alt only.
    block = _build(tmp_path, "", {"name-top-left-both": "Both"})
    assert ADVERT not in block, "-both-only label fired the advert cue"


@pytest.mark.parametrize(
    "both_label",
    [
        "name-top-left-both",
        "name-top-right-both",
        "name-bottom-right-both",
        "name-bottom-left-both",
        "purpose-top-left-both",
        "purpose-top-right-both",
        "purpose-bottom-right-both",
        "purpose-bottom-left-both",
        "axis-label-top-both",
        "axis-label-bottom-both",
        "axis-label-left-both",
        "axis-label-right-both",
        "need-top-left-both",
        "need-top-right-both",
        "need-bottom-right-both",
        "need-bottom-left-both",
    ],
)
def test_each_both_label_renders_plain_and_no_cue(tmp_path: Path, both_label: str):
    block = _build(tmp_path, "", {both_label: "B"})
    # The span must not carry label-swappable or label-alt (only the plain
    # class for its slot type). Assert neither swap class appears on any
    # span — the -both label is plain.
    assert " label-swappable" not in block or ADVERT in block, \
        f"{both_label}: label-swappable appeared (should be plain)"
    assert '<span class="' in block, f"{both_label}: no span rendered"
    assert ADVERT not in block, f"{both_label}: -both fired the advert cue"


# --- -both half-annotations render plain -------------------------------

def test_both_half_annotation_renders_plain(tmp_path: Path):
    block = _build(tmp_path, "", {"top-half-both": "Always top"})
    assert "annotation-top-half" in block, block
    # The -both block has no label-swappable / label-alt class on its div.
    assert 'annotation-top-half label-swappable' not in block, \
        "label-swappable on a -both half-annotation"
    assert 'annotation-top-half label-alt' not in block, \
        "label-alt on a -both half-annotation"
    assert ADVERT not in block, "-both half-annotation fired the advert cue"


def test_both_half_annotation_always_visible_text(tmp_path: Path):
    block = _build(tmp_path, "", {"top-half-both": "Always visible"})
    assert "Always visible" in block, block


# --- Global label swap: a default with no own -alt still swaps ---------

def test_global_swap_default_fades_when_other_label_has_alt(tmp_path: Path):
    # name-top-left (default, no own -alt) + name-top-right-alt (different
    # label). Under the global swap, label_swap_active is True
    # (name-top-right-alt is an -alt), so the name-top-left default gains
    # label-swappable and fades on hover even though it has no own -alt.
    block = _build(tmp_path, "", {
        "name-top-left": "Default", "name-top-right-alt": "Alt right",
    })
    assert '<span class="type label-swappable">Default</span>' in block, block
    assert '<span class="type label-alt">Alt right</span>' in block, block


def test_global_swap_purpose_label_fades_when_axis_label_has_alt(tmp_path: Path):
    # A purpose label (default) fades when an axis-label -alt is present —
    # the swap is global across label kinds, not per-slot.
    block = _build(tmp_path, "", {
        "purpose-top-left": "Purpose default", "axis-label-top-alt": "Axis alt",
    })
    assert '<span class="purpose label-swappable">Purpose default</span>' in block, block


def test_no_alt_no_global_swap_default_is_plain(tmp_path: Path):
    # No -alt anywhere => label_swap_active is False => default is plain.
    block = _build(tmp_path, "", {"name-top-left": "Default", "name-top-right": "Right"})
    assert '<span class="type">Default</span>' in block, block
    assert '<span class="type label-swappable">' not in block, block


# --- -both stays visible when label_swap_active is true ----------------

def test_both_stays_plain_when_other_label_has_alt(tmp_path: Path):
    # name-top-left-both (plain, always visible) + name-top-right-alt
    # (triggers label_swap_active). The -both label must NOT gain
    # label-swappable (it stays visible on hover); the -alt label still gets
    # label-alt.
    block = _build(tmp_path, "", {
        "name-top-left-both": "Always", "name-top-right-alt": "Alt right",
    })
    assert '<span class="type">Always</span>' in block, block
    assert '<span class="type label-swappable">Always</span>' not in block, \
        "-both label gained label-swappable (should stay plain/visible)"
    assert '<span class="type label-alt">Alt right</span>' in block, block
    # The advert cue fires (name-top-right-alt is an -alt).
    assert ADVERT in block, "advert cue missing with -alt present"


def test_both_half_stays_plain_when_other_label_has_alt(tmp_path: Path):
    block = _build(tmp_path, "", {
        "top-half-both": "Always top", "left-half-alt": "Alt left",
    })
    assert 'annotation-top-half label-swappable' not in block, \
        "-both half-annotation gained label-swappable"
    assert 'annotation-top-half label-alt' not in block, \
        "-both half-annotation gained label-alt"
    assert "Always top" in block, block
    assert ADVERT in block, "advert cue missing with left-half-alt present"


# --- All three: default + alt + both -----------------------------------

def test_default_alt_both_renders_all_three_spans(tmp_path: Path):
    # name-top-left (default, swappable) + name-top-left-alt (label-alt) +
    # name-top-left-both (plain, always visible). All three spans render with
    # the right classes.
    block = _build(tmp_path, "", {
        "name-top-left": "Default", "name-top-left-alt": "Alt", "name-top-left-both": "Both",
    })
    assert '<span class="type label-swappable">Default</span>' in block, block
    assert '<span class="type label-alt">Alt</span>' in block, block
    assert '<span class="type">Both</span>' in block, block
    assert ADVERT in block, "advert cue missing with -alt present"


def test_default_alt_both_half_annotations_render_all_three(tmp_path: Path):
    block = _build(tmp_path, "", {
        "top-half": "Default half", "top-half-alt": "Alt half",
        "top-half-both": "Both half",
    })
    assert 'annotation-top-half label-swappable' in block, \
        "default half-annotation missing label-swappable"
    assert 'annotation-top-half label-alt' in block, \
        "alt half-annotation missing label-alt"
    # The -both block is plain (no label-swappable / label-alt).
    assert "Both half" in block, block
    assert ADVERT in block, "advert cue missing with half-alt present"


# --- Axis-line -alt makes ALL default elements swap (strict fade-out) --

def test_axis_line_alt_makes_labels_swap(tmp_path: Path):
    # x-axis-alt (an axis-line -alt) enables the hover state, so ALL default
    # elements fade out on hover — content labels and axis labels included —
    # even with no -alt replacement (strict fade-out).
    block = _build(tmp_path, "x-axis-alt", {
        "name-top-left": "Default", "axis-label-top": "Axis label",
    })
    assert '<span class="type label-swappable">Default</span>' in block, block
    assert '<span class="axis label-swappable">Axis label</span>' in block, block
    # The advert cue fires (axis-line -alt present).
    assert ADVERT in block, "advert cue missing with axis-line -alt"


# --- Label -alt makes the default axis lines swap (strict fade-out) ----

def test_label_alt_makes_axis_lines_swap(tmp_path: Path):
    # x-axis (default) + name-top-left-alt (a label -alt). The label -alt
    # enables the hover state, so the default x-axis line is swappable too.
    block = _build(tmp_path, "x-axis", {"name-top-left-alt": "Alt"})
    assert '<div class="axis-line x-axis label-swappable">' in block, block
    assert '<span class="type label-alt">Alt</span>' in block, block
    assert ADVERT in block, "advert cue missing with label -alt present"
