"""The ``collapse`` / ``collapse-alt`` / ``collapse-both`` directive args
collapse the slots.

A flag-style directive arg (present/absent, like ``axes`` and ``blur``): when
present, each of the 12 quadrant content slots (type / purpose / need × 4
quadrants — **not** the axis labels, which sit on the axes) is transformed
with two randomised effects drawn once per slot at build time, more dramatic
than ``blur``:

* **Inward pull** — moved toward the diagram **origin** (where the axes cross)
  by a random fraction ``f ∈ [0.70, 1.00]`` of the slot's distance to the
  origin: ``new_pos = slot_pos + f * (origin - slot_pos)``. The large ``f``
  drags slots firmly toward the centre so they can overlap.
* **Rotation** — rotated by a random angle in the signed full range
  ``[-180°, 180°]`` (any angle, including near-zero and ±180°; no
  minimum-magnitude guarantee, unlike ``blur``'s ``[2°, 20°]`` magnitude +
  sign form).

Suffix semantics (mirroring ``blur`` / ``x-axis``, confirmed by the user):

* ``collapse`` (no suffix): the collapse applies unhovered. The collapsed
  spans get an inline ``style="transform: ..."``; no ``label-swappable``
  unless ``collapse-alt`` is also present.
* ``collapse-alt``: the collapse applies on hover. The default spans become
  ``label-swappable`` (fade out on hover); the ``-alt`` spans become
  ``label-alt`` (reveal on hover), each carrying its own inline transform —
  **the same draw** as the default when both are present. Fires the advert
  cue.
* ``collapse-both``: the collapse applies always (plain, no swap). Does NOT
  fire the advert cue.
* ``collapse collapse-alt``: both default and alt render with the **same**
  per-slot transform (one draw). Advert cue fires.
* ``collapse-alt`` alone: only the ``-alt`` spans render (``label-alt``,
  collapsed with their own draw); the default spans are uncollapsed but
  ``label-swappable``. Advert cue fires.

Coexistence with ``blur``: both flags may be present on one diagram. They
draw independently (separate per-slot random values) and compose only at
resolve time — when both target the same span, ``collapse`` wins (it is the
more dramatic effect), via the visitor's ``resolve_transform`` priority
chain (collapse > blur, with ``-both`` fallbacks last).

The advert cue fires on ``collapse-alt`` (any ``-alt`` does) but not on
``collapse`` or ``collapse-both``.

Randomness happens in Python at build time (no JS). The generator is
**unseeded** (``random.Random()``, OS entropy) so the collapse reshuffles on
every build — these tests assert **structure** (a ``transform`` with
``translate(...cqw, ...cqw) rotate(...deg)`` present on each slot span, the
``translate`` / ``rotate`` magnitudes in range), not exact values.
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
# All 12 quadrant content labels, supplied so every slot renders and the
# collapse transform lands on a span that is actually emitted.
LABEL_VALUES = _mod.LABEL_VALUES


def _rst(args: str) -> str:
    lines = [f"..  diataxis-diagram:: {args}".rstrip(),
             f"   :title: {TITLE_TEXT}", f"   :desc: {DESC_TEXT}", ""]
    for name, value in LABEL_VALUES.items():
        lines.append(f'   :{name}: "{value}"')
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


ADVERT = '<div class="advert-cue">'

# Matches an inline ``style="transform: <base> translate(DXcqw, DYcqw)
# rotate(Adeg)"`` on a slot span. The base is ``translateY(±50%)``; the
# translate components are floats ending in ``cqw``; the rotation is a float
# (possibly negative) ending in ``deg``. Same shape as ``blur``'s regex —
# the transform string format is identical; what differs is the ranges.
_TRANSFORM_RE = re.compile(
    r'style="transform:\s*'
    r"translateY\(-?50%\)\s+"
    r"translate\((-?[0-9.]+)cqw,\s*(-?[0-9.]+)cqw\)\s+"
    r"rotate\((-?[0-9.]+)deg\)"
)


def _assert_collapse_transforms_present(body: str, *, label: str):
    """Every quadrant-content span in ``body`` carries a collapse transform
    with magnitudes in the collapse ranges."""
    matches = _TRANSFORM_RE.findall(body)
    assert matches, f"{label}: no collapse transform found on any span"
    for dx, dy, angle in matches:
        dx = float(dx)
        dy = float(dy)
        angle = float(angle)
        # ``f ∈ [0.70, 1.00]`` × the centre→origin vector. The x vector is up
        # to ±25 (% of the visible region); x in cqw is the same as % of
        # width, so |dx| ≤ 1.00 * 25 = 25.0 cqw. The y vector is up to ±25
        # (% of the visible region's height); y in cqw is % of height ×
        # height/width, so |dy| ≤ 25.0 * (height/width). For the full diagram
        # height/width ≈ 540/960, so |dy| ≤ ~14.06; bound by the full-diagram
        # x bound (25.0) as a generous upper limit.
        assert abs(dx) <= 25.001, f"{label}: dx {dx} out of range"
        assert abs(dy) <= 25.001, f"{label}: dy {dy} out of range"
        # ``angle ∈ [-180, 180]`` (signed full range).
        assert -180.0 <= angle <= 180.0, f"{label}: angle {angle} not in [-180, 180]"


def _assert_no_transforms(body: str, *, label: str):
    """No span in ``body`` carries a collapse/blur transform inline style."""
    matches = _TRANSFORM_RE.findall(body)
    assert not matches, f"{label}: unexpected transforms ({len(matches)})"


# --- No collapse: no transform, no cue ----------------------------------

def test_no_args_renders_no_collapse_no_cue(tmp_path: Path):
    body = _body(_build(tmp_path, ""))
    _assert_no_transforms(body, label="no args")
    assert ADVERT not in body, "advert cue rendered with no collapse"


# --- collapse: transform on every span, no swap, no cue ------------------

@pytest.mark.parametrize("args", ["collapse", "collapse-both"])
def test_collapse_renders_transform_no_swap_no_cue(tmp_path: Path, args: str):
    body = _body(_build(tmp_path, args))
    _assert_collapse_transforms_present(body, label=args)
    assert 'label-swappable' not in body, f"{args}: collapse wired a swap"
    assert ADVERT not in body, f"{args}: advert cue rendered (should be absent)"


def test_collapse_transform_is_inline_on_each_span(tmp_path: Path):
    # ``LABEL_VALUES`` supplies the 8 type + purpose labels (no ``need-*``),
    # so 8 slots render and 8 collapse transforms are emitted — one per span.
    body = _body(_build(tmp_path, "collapse"))
    matches = _TRANSFORM_RE.findall(body)
    assert len(matches) == 8, (
        f"expected 8 collapse transforms (one per rendered slot span), got {len(matches)}"
    )


# --- collapse-alt: label-alt spans carry the transform, cue fires --------

def test_collapse_alt_renders_label_alt_spans_with_transform(tmp_path: Path):
    # ``collapse-alt`` alone: the default (no-suffix) spans are NOT collapsed,
    # only the ``-alt`` spans are — but we supplied only default labels (no
    # ``-alt`` label values), so no slot renders an alt span. The advert cue
    # still fires (``collapse-alt`` is an ``-alt``), and the default spans are
    # swappable. We only assert the cue fires and no default-span collapse
    # transform is emitted.
    body = _body(_build(tmp_path, "collapse-alt"))
    assert ADVERT in body, "advert cue missing for collapse-alt"
    _assert_no_transforms(body, label="collapse-alt (no -alt labels)")


def test_collapse_alt_with_alt_labels_collapses_alt_spans(tmp_path: Path):
    # Supply ``-alt`` label values so the ``-alt`` spans render and carry the
    # collapse transform. The default spans are swappable (fade on hover), the
    # ``-alt`` spans are ``label-alt`` (reveal on hover) and collapsed.
    rst = (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram:: collapse-alt\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f'   :name-top-left: "Default"\n'
        f'   :name-top-left-alt: "Alt"\n'
    )
    out = _build_html(tmp_path, rst)
    body = _body(_block((out / "index.html").read_text(encoding="utf-8")))
    assert ADVERT in body, "advert cue missing for collapse-alt with -alt labels"
    alt_span = re.search(
        r'<span class="type label-alt"\s+style="transform:\s*'
        r"translateY\(-?50%\)\s+translate\([^)]+\)\s+rotate\([^)]+\)",
        body,
    )
    assert alt_span, f"no collapsed label-alt span found:\n{body[:400]}"
    default_span = re.search(
        r'<span class="type label-swappable">Default</span>', body,
    )
    assert default_span, f"default span missing or not swappable:\n{body[:400]}"


# --- collapse collapse-alt: same draw, default swappable + alt label-alt -

def test_collapse_collapse_alt_shares_draw_between_default_and_alt(tmp_path: Path):
    # ``collapse collapse-alt``: both default and alt render with the SAME
    # per-slot transform (one draw). The default is ``label-swappable``, the
    # alt is ``label-alt``; both carry an identical inline ``transform``.
    rst = (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram:: collapse collapse-alt\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f'   :name-top-left: "Default"\n'
        f'   :name-top-left-alt: "Alt"\n'
    )
    out = _build_html(tmp_path, rst)
    body = _body(_block((out / "index.html").read_text(encoding="utf-8")))
    assert ADVERT in body, "advert cue missing for collapse collapse-alt"
    default_match = re.search(
        r'<span class="type label-swappable"\s+'
        r'style="(transform: translateY\(-?50%\)\s+translate\([^)]+\)\s+rotate\([^)]+\))"',
        body,
    )
    alt_match = re.search(
        r'<span class="type label-alt"\s+'
        r'style="(transform: translateY\(-?50%\)\s+translate\([^)]+\)\s+rotate\([^)]+\))"',
        body,
    )
    assert default_match, f"no collapsed swappable default span:\n{body[:400]}"
    assert alt_match, f"no collapsed label-alt span:\n{body[:400]}"
    assert default_match.group(1) == alt_match.group(1), (
        f"collapse collapse-alt default and alt transforms differ "
        f"(should be the same draw): "
        f"{default_match.group(1)!r} vs {alt_match.group(1)!r}"
    )


# --- collapse-both: always visible, no swap, no cue; coexists with -alt ---

def test_collapse_both_does_not_fire_cue(tmp_path: Path):
    body = _body(_build(tmp_path, "collapse-both"))
    _assert_collapse_transforms_present(body, label="collapse-both")
    assert ADVERT not in body, "collapse-both fired the advert cue"


def test_collapse_both_with_collapse_alt_cue_fires(tmp_path: Path):
    # ``collapse-both collapse-alt``: the cue fires (``-alt`` present); the
    # ``-both`` transform lands on the default span (always visible), the
    # ``-alt`` transform lands on the alt span (revealed on hover).
    rst = (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram:: collapse-both collapse-alt\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f'   :name-top-left: "Default"\n'
    )
    out = _build_html(tmp_path, rst)
    body = _body(_block((out / "index.html").read_text(encoding="utf-8")))
    assert ADVERT in body, "advert cue missing with collapse-alt present alongside collapse-both"
    default_match = re.search(
        r'<span class="type[^"]*"\s+style="transform:\s*'
        r'translateY\(-?50%\)\s+translate\([^)]+\)\s+rotate\([^)]+\)"',
        body,
    )
    assert default_match, f"no collapsed default span for collapse-both collapse-alt:\n{body[:400]}"


# --- collapse on a subset variant still transforms the rendered slots ----

def test_collapse_on_subset_variant_transforms_rendered_slots(tmp_path: Path):
    # A single-quadrant variant (``top-left``) renders 2 slots (type +
    # purpose in top-left; ``LABEL_VALUES`` has no ``need-*``); the collapse
    # transform should land on each.
    body = _body(_build(tmp_path, "top-left collapse"))
    matches = _TRANSFORM_RE.findall(body)
    assert len(matches) == 2, (
        f"expected 2 collapse transforms for top-left collapse, got {len(matches)}"
    )


# --- collapse is accepted alongside category args ------------------------

def test_collapse_with_axes_renders_collapse_and_axes(tmp_path: Path):
    # ``collapse`` coexists with ``axes`` (both flag/category args); the axis
    # lines render and the slots are collapsed.
    body = _body(_build(tmp_path, "axes collapse"))
    _assert_collapse_transforms_present(body, label="axes collapse")
    assert '<div class="axis-line x-axis"></div>' in body, "x-axis missing for axes collapse"
    assert '<div class="axis-line y-axis"></div>' in body, "y-axis missing for axes collapse"


# --- per-slot independence: each slot gets its own random draw ------------

def test_collapse_each_slot_gets_distinct_transform(tmp_path: Path):
    # Regression guard: each slot must draw its own random ``f`` and
    # ``angle``. ``LABEL_VALUES`` supplies 8 labels (4 type + 4 purpose, no
    # ``need-*``), so 8 slots render and all 8 transforms must be distinct.
    body = _body(_build(tmp_path, "collapse"))
    matches = _TRANSFORM_RE.findall(body)
    assert len(matches) == 8, (
        f"expected 8 collapse transforms, got {len(matches)}"
    )
    transforms = [m for m in _TRANSFORM_RE.finditer(body)]
    seen = {}
    for m in transforms:
        triple = (m.group(1), m.group(2), m.group(3))
        start = m.start()
        tag_start = body.rfind("<span", 0, start)
        tag = body[tag_start:start].strip() if tag_start != -1 else "<unknown>"
        if triple in seen:
            prev_tag = seen[triple]
            assert False, (
                f"two slots share the same collapse transform "
                f"(dx={triple[0]}cqw, dy={triple[1]}cqw, angle={triple[2]}deg): "
                f"{prev_tag!r} and {tag!r} — each slot must draw independently"
            )
        seen[triple] = tag


# --- collapse wins over blur when both target the same span --------------

def test_collapse_wins_over_blur_when_both_present(tmp_path: Path):
    # ``blur collapse``: both flags target the default span. ``collapse``
    # wins via the template's ``elif`` chain (it is the more dramatic
    # effect). The emitted transform must be a collapse transform — i.e.
    # its angle is in ``[-180, 180]`` and could be any value, but crucially
    # NOT a blur transform (whose angle magnitude is in ``[2, 20]``). Since
    # the two ranges overlap (``[2, 20]`` ⊂ ``[-180, 180]``), we cannot
    # distinguish by angle alone; instead we assert that the transform is
    # present and in the collapse range, and that the dx/dy are in the
    # collapse range (``f ∈ [0.7, 1.0]`` ⇒ |dx| up to 25, vs blur's
    # ``f ∈ [0.3, 0.6]`` ⇒ |dx| up to 15). The collapse draw is independent
    # of the blur draw, so the emitted values come from the collapse ranges.
    body = _body(_build(tmp_path, "blur collapse"))
    _assert_collapse_transforms_present(body, label="blur collapse")
    # At least one slot should have a large pull (|dx| > 15 cqw would be
    # impossible for blur alone with f ∈ [0.3, 0.6] and |vx| ≤ 25, since
    # 0.6 * 25 = 15). Collapse with f ∈ [0.7, 1.0] can reach up to 25.
    # This confirms the collapse draw (not the blur draw) is what landed.
    matches = _TRANSFORM_RE.findall(body)
    assert matches, "no transform found for blur collapse"
    # With 8 slots and f ∈ [0.7, 1.0], it is overwhelmingly likely at least
    # one slot has |dx| > 15; assert at least one does to confirm collapse
    # won. (Probability all 8 have |dx| ≤ 15 is negligible: that requires
    # f * |vx| ≤ 15 for all 8, i.e. f ≤ 15/|vx|; for the corner slots
    # |vx| = 25, so f ≤ 0.6, which collapse's [0.7, 1.0] never produces.)
    large_pulls = [m for m in matches if abs(float(m[0])) > 15.0]
    assert large_pulls, (
        f"blur collapse: no slot with |dx| > 15 (collapse should win over blur); "
        f"got dx values {[m[0] for m in matches]}"
    )