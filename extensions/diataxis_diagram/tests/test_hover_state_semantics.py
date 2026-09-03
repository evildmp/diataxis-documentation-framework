"""Hover/tap-state semantics, as documented in ``technical-guide.rst``.

The documented spec:

* A diagram has an optional hover/tap state, only enabled when at least one
  argument or option has an ``-alt`` suffix. Every argument and content option
  accepts the suffix.
* A ``-both`` suffix means that the argument/option applies in both states.
* If the hover/tap state is enabled, then nothing applies to it that has not
  been selected with ``-alt`` or ``-both``.

Semantics (confirmed by the user):

* **Strict fade-out.** When the hover state is enabled (any ``-alt`` anywhere),
  EVERY unsuffixed element fades out on hover, even with no ``-alt``
  replacement. E.g. ``x-axis-alt`` alone: on hover all labels and the y-axis
  line vanish; the hover state shows only the alt x-axis line + cue. So
  ``label_swap_active`` and the axis-line swap must key off the same condition
  that fires the advert cue (any ``-alt``), not off narrower per-element
  conditions.
* **``-both`` applies in the hovered state too.** An effect belongs to a state:
  normal, hovered (``-alt``) or both (``-both``). When the hovered state has no
  ``-alt`` transform of its own, it falls back to the ``-both`` transform; and
  the always-shown ``-both`` content span carries the ``-both`` transform in
  both states. ``-both`` still never switches the hover state on.
* **Tap works on touch screens.** The reveal must not rely on ``:hover``
  alone: a ``@media (hover: none)`` block keys the same reveal on ``:focus``
  (tap focuses the ``tabindex="0"`` root; tapping elsewhere blurs it). No
  unconditional ``:focus`` rule outside that media block (desktop click-latch
  bug, fixed 2026-08-24); ``:focus-visible`` stays for keyboard users.

Quadrant ``-alt`` args (e.g. ``top-left-alt``) remain a no-op (see
``test_axis_line_alt_args``) and never enable the hover state.
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
ALL_LABEL_VALUES = _mod.LABEL_VALUES


def _rst(args: str, labels: dict[str, str] | None = None) -> str:
    lines = [f"..  diataxis-diagram:: {args}".rstrip(),
             f"   :title: {TITLE_TEXT}", f"   :desc: {DESC_TEXT}", ""]
    for name, value in (labels or {}).items():
        lines.append(f'   :{name}: "{value}"')
    return "Welcome\n=======\n\n" + "\n".join(lines) + "\n"


def _block(html: str) -> str:
    blocks = _diagram_blocks(html)
    assert len(blocks) == 1, f"expected one diagram, got {len(blocks)}"
    return blocks[0]


def _build(tmp_path: Path, args: str, labels: dict[str, str] | None = None) -> str:
    out = _build_html(tmp_path, _rst(args, labels))
    return _block((out / "index.html").read_text(encoding="utf-8"))


def _body(block: str) -> str:
    """The block with its ``<style>`` stripped, so substring assertions hit
    real tags rather than CSS selectors that mention the same class names."""
    return re.sub(r"<style>.*?</style>", "", block, flags=re.DOTALL)


ADVERT = '<div class="advert-cue">'
X_SWAPPABLE = '<div class="axis-line x-axis label-swappable"></div>'
Y_SWAPPABLE = '<div class="axis-line y-axis label-swappable"></div>'
X_DEFAULT = '<div class="axis-line x-axis"></div>'

# An inline blur/collapse transform on a span (base centring translate +
# pull translate + rotate; values are random, so match structurally).
_TRANSFORM_STYLE = (
    r'style="transform: translateY\(-?50%\)\s+'
    r"translate\([^)]+\)\s+rotate\([^)]+\)"
)


# --- Strict fade-out: any -alt makes ALL default elements swappable ------

def test_axis_alt_alone_makes_default_labels_swappable(tmp_path: Path):
    # ``x-axis-alt`` alone: hover state enabled by the axis-line -alt, so the
    # default labels must fade out on hover (strict fade-out) even though
    # nothing replaces them.
    body = _body(_build(tmp_path, "x-axis-alt", {"name-top-left": "Tutorials"}))
    assert '<span class="type label-swappable">Tutorials</span>' in body, (
        f"default label not swappable with x-axis-alt present:\n{body[:600]}"
    )


def test_blur_alt_makes_default_axis_lines_swappable(tmp_path: Path):
    # ``axes blur-alt``: hover state enabled by the blur -alt, so the default
    # axis lines (not just labels) must fade out on hover.
    body = _body(_build(tmp_path, "axes blur-alt"))
    assert X_SWAPPABLE in body, "x-axis default line not swappable with blur-alt"
    assert Y_SWAPPABLE in body, "y-axis default line not swappable with blur-alt"


def test_collapse_alt_alone_makes_default_labels_swappable(tmp_path: Path):
    # ``collapse-alt`` alone enables the hover state like any other -alt.
    body = _body(_build(tmp_path, "collapse-alt", {"name-top-left": "Tutorials"}))
    assert '<span class="type label-swappable">Tutorials</span>' in body, (
        f"default label not swappable with collapse-alt present:\n{body[:600]}"
    )


def test_label_alt_makes_default_axis_lines_swappable(tmp_path: Path):
    # A label -alt enables the hover state, so the default axis lines must
    # swap too (strict fade-out applies to every element class).
    labels = {"name-top-left": "Tutorials", "name-top-left-alt": "Hover"}
    body = _body(_build(tmp_path, "axes", labels))
    assert X_SWAPPABLE in body, "x-axis default line not swappable with label -alt"
    assert Y_SWAPPABLE in body, "y-axis default line not swappable with label -alt"


# --- -both never switches the hover state on -----------------------------

def test_blur_both_alone_no_hover_state(tmp_path: Path):
    # ``blur-both`` alone: the transform applies always (plain), but no hover
    # state: no advert cue, no swap classes, no alt spans.
    body = _body(_build(tmp_path, "blur-both", ALL_LABEL_VALUES))
    assert ADVERT not in body, "blur-both fired the advert cue"
    assert "label-swappable" not in body, "blur-both wired a swap"
    assert "label-alt" not in body, "blur-both rendered an alt span"
    # The -both transform still lands on the default spans (always visible).
    matches = re.findall(_TRANSFORM_STYLE, body)
    assert len(matches) == 8, (
        f"expected 8 blur-both transforms (one per rendered span), got {len(matches)}"
    )


def test_no_alt_no_both_no_swap_no_cue(tmp_path: Path):
    # No -alt/--both anywhere: nothing is swappable, no cue.
    body = _body(_build(tmp_path, "axes", {"name-top-left": "Tutorials"}))
    assert X_DEFAULT in body, "x-axis default line missing"
    assert X_SWAPPABLE not in body, "swap wired with no -alt"
    assert "label-swappable" not in body, "swap wired with no -alt"
    assert ADVERT not in body, "advert cue fired with no -alt"


# --- -both applies in the hovered state too ------------------------------

def test_blur_both_transform_falls_back_to_alt_span(tmp_path: Path):
    # ``blur-both`` + a label -alt: the hovered state has no blur-alt of its
    # own, so the alt span falls back to the -both transform.
    labels = {"name-top-left": "Default", "name-top-left-alt": "Alt"}
    body = _body(_build(tmp_path, "blur-both", labels))
    alt_span = re.search(
        rf'<span class="type label-alt" {_TRANSFORM_STYLE}">Alt</span>', body
    )
    assert alt_span, (
        f"label-alt span missing the -both blur transform:\n{body[:600]}"
    )


def test_blur_both_transform_applies_to_both_span(tmp_path: Path):
    # A ``-both`` content label + ``blur-both``: the always-shown both span
    # carries the -both transform (in both states).
    body = _body(_build(tmp_path, "blur-both", {"name-top-left-both": "Both"}))
    both_span = re.search(
        rf'<span class="type" {_TRANSFORM_STYLE}">Both</span>', body
    )
    assert both_span, (
        f"-both span missing the blur-both transform:\n{body[:600]}"
    )


# --- Tap: touch interaction via :focus inside @media (hover: none) -------

def test_tap_focus_rules_in_hover_none_media_block():
    css = _mod.shared_css()
    media = re.search(r"@media \(hover: none\)\s*\{(.*?)\n\}", css, re.DOTALL)
    assert media, "no @media (hover: none) block for touch interaction"
    block = media.group(1)
    assert ".diagram-root:focus .label-swappable" in block, (
        "tap: :focus does not fade out swappable elements"
    )
    assert ".diagram-root:focus .label-alt" in block, (
        "tap: :focus does not reveal alt elements"
    )
    assert ".diagram-root:focus .advert-cue" in block, (
        "tap: :focus does not hide the advert cue"
    )
    # Guard the 2026-08-24 fix: no bare :focus outside the media block
    # (it would latch the hover state on desktop click). Comments are
    # stripped first — prose may mention :focus without being a rule.
    outside = css[: media.start()] + css[media.end():]
    outside = re.sub(r"/\*.*?\*/", "", outside, flags=re.DOTALL)
    stray = re.search(r":focus(?!-visible)", outside)
    assert not stray, (
        f"bare :focus outside @media (hover: none) at offset {stray.start()}"
    )


# --- The hover state is enabled by exactly one -alt anywhere -------------

@pytest.mark.parametrize("args", [
    "x-axis-alt",
    "y-axis-alt",
    "axes-alt",
    "blur-alt",
    "collapse-alt",
])
def test_any_alt_enables_hover_state(tmp_path: Path, args: str):
    # Whichever -alt enables the state, the cue fires and default labels fade.
    body = _body(_build(tmp_path, args, {"name-top-left": "Tutorials"}))
    assert ADVERT in body, f"{args}: advert cue missing"
    assert '<span class="type label-swappable">Tutorials</span>' in body, (
        f"{args}: default label not swappable"
    )
