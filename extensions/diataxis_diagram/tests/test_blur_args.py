"""The ``blur`` / ``blur-alt`` / ``blur-both`` directive args blur the slots.

A flag-style directive arg (present/absent, like ``axes``): when present, each
of the 12 quadrant content slots (type / purpose / need × 4 quadrants — **not**
the axis labels, which sit on the axes) is transformed with two randomized
effects drawn once per slot at build time:

* **Inward pull** — moved toward the diagram **origin** (where the axes cross)
  by a random fraction ``f ∈ [0.3, 0.5]`` of the slot's distance to the
  origin: ``new_pos = slot_pos + f * (origin - slot_pos)``.
* **Rotation** — rotated by a random angle drawn directly from the signed
  range ``[-5°, 5°]``, including angles near zero (no minimum magnitude).

Suffix semantics (mirroring ``x-axis`` / ``x-axis-alt`` / ``x-axis-both``,
confirmed by the user):

* ``blur`` (no suffix): the blur applies unhovered. The blurred spans get an
  inline ``style="transform: ..."``; no ``label-swappable`` (it is not an
  interactive swap unless ``blur-alt`` is also present).
* ``blur-alt``: the blur applies on hover. The default (no-suffix) spans become
  ``label-swappable`` (fade out on hover) and the ``-alt`` spans become
  ``label-alt`` (reveal on hover), each carrying its own inline transform —
  **the same draw** as the default when both are present (one random draw
  shared between the two states). Fires the advert cue.
* ``blur-both``: the blur applies always (plain, no swap classes). Does NOT
  fire the advert cue.
* ``blur blur-alt``: both default and alt render with the **same** per-slot
  random transform (one draw); the default is ``label-swappable`` and the alt
  is ``label-alt``. Advert cue fires (``-alt`` present).
* ``blur-alt`` alone: only the ``-alt`` spans render (``label-alt``); their
  own draw. Advert cue fires.

The advert cue (see ``test_advert_cue``) fires on ``blur-alt`` (any ``-alt``
does) but not on ``blur`` or ``blur-both``.

Randomness happens in Python at build time (no JS; the diagram is pure
HTML/CSS). The generator is **unseeded** (``random.Random()``, OS entropy) so
the blur reshuffles on every build — these tests assert **structure** (a
``transform`` with ``translate(...cqw, ...cqw) rotate(...deg)`` present on each
slot span, the ``translate`` / ``rotate`` magnitudes in range), not exact
values (per the ``_diagram_id_counter`` note in ``__init__.py``).
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
# All 12 quadrant content labels, supplied so every slot renders and the blur
# transform lands on a span that is actually emitted.
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
# (possibly negative) ending in ``deg``.
_TRANSFORM_RE = re.compile(
    r'style="transform:\s*'
    r"translateY\(-?50%\)\s+"
    r"translate\((-?[0-9.]+)cqw,\s*(-?[0-9.]+)cqw\)\s+"
    r"rotate\((-?[0-9.]+)deg\)"
)


def _assert_blur_transforms_present(body: str, *, label: str):
    """Every quadrant-content span in ``body`` carries a blur ``transform``."""
    matches = _TRANSFORM_RE.findall(body)
    assert matches, f"{label}: no blur transform found on any span"
    for dx, dy, angle in matches:
        dx = float(dx)
        dy = float(dy)
        angle = float(angle)
        # ``f ∈ [0.3, 0.5]`` × the centre→origin vector. The x vector is up to
        # ±25 (% of the visible region); x in cqw is the same as % of width, so
        # |dx| ≤ 0.5 * 25 = 12.5 cqw. The y vector is up to ±25 (% of the visible
        # region's height); y in cqw is % of height × height/width, so |dy| ≤
        # 12.5 * (height/width). For the full diagram height/width ≈ 540/960,
        # so |dy| ≤ ~7.03; for subset variants the ratio can differ, so bound
        # it by the full-diagram x bound (12.5) as a generous upper limit.
        assert abs(dx) <= 12.501, f"{label}: dx {dx} out of range"
        assert abs(dy) <= 12.501, f"{label}: dy {dy} out of range"
        assert -5.0 <= angle <= 5.0, f"{label}: angle {angle} not in [-5, 5]"


def _assert_no_blur_transforms(body: str, *, label: str):
    """No span in ``body`` carries a blur ``transform`` inline style."""
    matches = _TRANSFORM_RE.findall(body)
    assert not matches, f"{label}: unexpected blur transforms ({len(matches)})"


# --- No blur: no transform, no cue --------------------------------------

def test_no_args_renders_no_blur_no_cue(tmp_path: Path):
    body = _body(_build(tmp_path, ""))
    _assert_no_blur_transforms(body, label="no args")
    assert ADVERT not in body, "advert cue rendered with no blur"


# --- blur: transform on every span, no swap, no cue ---------------------

@pytest.mark.parametrize("args", ["blur", "blur-both"])
def test_blur_renders_transform_no_swap_no_cue(tmp_path: Path, args: str):
    body = _body(_build(tmp_path, args))
    _assert_blur_transforms_present(body, label=args)
    # No label-alt / label-swappable on the blurred spans: the blur transform
    # is applied plain (always visible), so no swap classes and no advert cue.
    # The blur transform is on a plain span (``class="type"``/``.purpose``/
    # ``.need``), not on a ``label-alt`` / ``label-swappable`` span.
    assert 'label-swappable' not in body, f"{args}: blur wired a swap"
    assert ADVERT not in body, f"{args}: advert cue rendered (should be absent)"


def test_blur_transform_is_inline_on_each_span(tmp_path: Path):
    # The transform must be on the span itself (inline ``style``), not on the
    # slot ``<div>`` — the span is the absolutely-positioned element whose
    # ``transform`` composes the blur with the centring ``translateY(±50%)``.
    # ``LABEL_VALUES`` supplies the 8 type + purpose labels (no ``need-*``),
    # so 8 slots render and 8 blur transforms are emitted — one per span.
    body = _body(_build(tmp_path, "blur"))
    matches = _TRANSFORM_RE.findall(body)
    assert len(matches) == 8, (
        f"expected 8 blur transforms (one per rendered slot span), got {len(matches)}"
    )


# --- blur-alt: label-alt spans carry the transform, cue fires -----------

def test_blur_alt_renders_label_alt_spans_with_transform(tmp_path: Path):
    # ``blur-alt`` alone: the default (no-suffix) spans are NOT blurred (no
    # ``blur`` default), only the ``-alt`` spans are — but we supplied only
    # default labels (no ``-alt`` label values), so no slot renders an alt
    # span. The advert cue still fires (``blur-alt`` is an ``-alt``), and the
    # default spans are swappable (``label_swap_active``), so they fade on
    # hover with nothing to replace them — the user's responsibility. We only
    # assert the cue fires and no default-span blur transform is emitted.
    body = _body(_build(tmp_path, "blur-alt"))
    assert ADVERT in body, "advert cue missing for blur-alt"
    # No default-span blur transform (the default spans are unblurred; the
    # ``-alt`` spans would carry the transform but no ``-alt`` labels are
    # supplied, so no ``-alt`` span renders).
    _assert_no_blur_transforms(body, label="blur-alt (no -alt labels)")


def test_blur_alt_with_alt_labels_blurs_alt_spans(tmp_path: Path):
    # Supply ``-alt`` label values so the ``-alt`` spans render and carry the
    # blur transform. The default spans are swappable (fade on hover), the
    # ``-alt`` spans are ``label-alt`` (reveal on hover) and blurred.
    rst = (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram:: blur-alt\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f'   :name-top-left: "Default"\n'
        f'   :name-top-left-alt: "Alt"\n'
    )
    out = _build_html(tmp_path, rst)
    body = _body(_block((out / "index.html").read_text(encoding="utf-8")))
    assert ADVERT in body, "advert cue missing for blur-alt with -alt labels"
    # The ``-alt`` span carries the blur transform (it is ``label-alt`` and
    # blurred); the default span is swappable but NOT blurred (no ``blur``
    # default arg). Find the alt span and assert it has a transform.
    alt_span = re.search(
        r'<span class="type label-alt"\s+style="transform:\s*'
        r"translateY\(-?50%\)\s+translate\([^)]+\)\s+rotate\([^)]+\)",
        body,
    )
    assert alt_span, f"no blurred label-alt span found:\n{body[:400]}"
    # The default span is swappable but unblurred.
    default_span = re.search(
        r'<span class="type label-swappable">Default</span>', body,
    )
    assert default_span, f"default span missing or not swappable:\n{body[:400]}"


# --- blur blur-alt: same draw, default swappable + alt label-alt --------

def test_blur_blur_alt_shares_draw_between_default_and_alt(tmp_path: Path):
    # ``blur blur-alt``: both default and alt render with the SAME per-slot
    # transform (one draw). The default is ``label-swappable``, the alt is
    # ``label-alt``; both carry an identical inline ``transform``.
    rst = (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram:: blur blur-alt\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f'   :name-top-left: "Default"\n'
        f'   :name-top-left-alt: "Alt"\n'
    )
    out = _build_html(tmp_path, rst)
    body = _body(_block((out / "index.html").read_text(encoding="utf-8")))
    assert ADVERT in body, "advert cue missing for blur blur-alt"
    # Both spans are blurred; the default is swappable, the alt is label-alt.
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
    assert default_match, f"no blurred swappable default span:\n{body[:400]}"
    assert alt_match, f"no blurred label-alt span:\n{body[:400]}"
    # Same draw → same transform string on both.
    assert default_match.group(1) == alt_match.group(1), (
        f"blur blur-alt default and alt transforms differ "
        f"(should be the same draw): "
        f"{default_match.group(1)!r} vs {alt_match.group(1)!r}"
    )


# --- blur-both: always visible, no swap, no cue; coexists with blur-alt --

def test_blur_both_does_not_fire_cue(tmp_path: Path):
    body = _body(_build(tmp_path, "blur-both"))
    _assert_blur_transforms_present(body, label="blur-both")
    assert ADVERT not in body, "blur-both fired the advert cue"


def test_blur_both_with_blur_alt_cue_fires(tmp_path: Path):
    # ``blur-both blur-alt``: the cue fires (``-alt`` present); the ``-both``
    # transform lands on the default span (always visible), the ``-alt``
    # transform lands on the alt span (revealed on hover). Edge case: the
    # default span also gains ``label-swappable`` (because ``label_swap_active``
    # is True from ``blur_alt``) and would fade on hover — the user's
    # responsibility (like ``x-axis-both x-axis-alt``); we only assert the cue
    # and that the default span carries a transform.
    rst = (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram:: blur-both blur-alt\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f'   :name-top-left: "Default"\n'
    )
    out = _build_html(tmp_path, rst)
    body = _body(_block((out / "index.html").read_text(encoding="utf-8")))
    assert ADVERT in body, "advert cue missing with blur-alt present alongside blur-both"
    # The default span carries a blur transform (from ``blur-both``).
    default_match = re.search(
        r'<span class="type[^"]*"\s+style="transform:\s*'
        r'translateY\(-?50%\)\s+translate\([^)]+\)\s+rotate\([^)]+\)"',
        body,
    )
    assert default_match, f"no blurred default span for blur-both blur-alt:\n{body[:400]}"


# --- blur on a subset variant still transforms the rendered slots -------

def test_blur_on_subset_variant_transforms_rendered_slots(tmp_path: Path):
    # A single-quadrant variant (``top-left``) renders 2 slots (type +
    # purpose in top-left; ``LABEL_VALUES`` has no ``need-*``); the blur
    # transform should land on each.
    body = _body(_build(tmp_path, "top-left blur"))
    matches = _TRANSFORM_RE.findall(body)
    assert len(matches) == 2, (
        f"expected 2 blur transforms for top-left blur, got {len(matches)}"
    )


# --- blur is accepted alongside category args --------------------------

def test_blur_with_axes_renders_blur_and_axes(tmp_path: Path):
    # ``blur`` coexists with ``axes`` (both flag/category args); the axis lines
    # render and the slots are blurred.
    body = _body(_build(tmp_path, "axes blur"))
    _assert_blur_transforms_present(body, label="axes blur")
    assert '<div class="axis-line x-axis"></div>' in body, "x-axis missing for axes blur"
    assert '<div class="axis-line y-axis"></div>' in body, "y-axis missing for axes blur"


# --- per-slot independence: each slot gets its own random draw ------------

def test_blur_each_slot_gets_distinct_transform(tmp_path: Path):
    # Regression guard: each slot must draw its own random ``f`` and ``angle``.
    # Previously the default/alt path drew once per *quadrant* (4 draws keyed
    # by ``_slot_centres``) and reused the same transform for all 3 slots in
    # that quadrant — so type and purpose in the same quadrant came out
    # identical. ``LABEL_VALUES`` supplies 8 labels (4 type + 4 purpose, no
    # ``need-*``), so 8 slots render and all 8 transforms must be distinct.
    body = _body(_build(tmp_path, "blur"))
    matches = _TRANSFORM_RE.findall(body)
    assert len(matches) == 8, (
        f"expected 8 blur transforms, got {len(matches)}"
    )
    transforms = [m for m in _TRANSFORM_RE.finditer(body)]
    # Each match's full transform string (the inline ``style`` value) should be
    # unique across all 8 slots. Two slots in the same quadrant sharing an
    # identical (dx, dy, angle) triple is the bug we are guarding against.
    seen = {}
    for m in transforms:
        triple = (m.group(1), m.group(2), m.group(3))
        # Find which span this transform sits on, for a useful failure message.
        # The match's start index lets us look back into ``body`` for the
        # opening ``<span ...`` tag.
        start = m.start()
        tag_start = body.rfind("<span", 0, start)
        tag = body[tag_start:start].strip() if tag_start != -1 else "<unknown>"
        if triple in seen:
            prev_tag = seen[triple]
            assert False, (
                f"two slots share the same blur transform "
                f"(dx={triple[0]}cqw, dy={triple[1]}cqw, angle={triple[2]}deg): "
                f"{prev_tag!r} and {tag!r} — each slot must draw independently"
            )
        seen[triple] = tag
