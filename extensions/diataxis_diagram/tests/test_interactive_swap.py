"""The interactive label-swap uses ``:focus-visible`` (not ``:focus-within``).

Hover or keyboard focus on the diagram swaps the default labels for their
``-alt`` variants by fading opacity. This was originally wired with
``:focus-within``, which **latches**: a click gives the diagram focus,
``:focus-within`` stays true after the mouse leaves, and the alt labels
never fade back out. The fix was to switch all three interactive-swap
rules to ``:focus-visible`` (keyboard focus only), which doesn't latch on
mouse click.

These tests pin that fix so it can't regress:

* the rendered CSS uses ``:focus-visible`` and not ``:focus-within`` in the
  interactive-swap rules;
* the opacity transitions are 1s ease on ``.label-alt`` and
  ``.label-swappable``;
* the inner div carries ``tabindex="0"`` so it can actually receive focus
  (without it ``:focus-visible`` can never fire and the swap is dead).
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


@pytest.fixture
def swap_block(tmp_path: Path) -> str:
    """A diagram with both a default and an -alt label (so swap is wired)."""
    out = _build_html(tmp_path, _rst({"name-top-left": "Default",
                                       "name-top-left-alt": "Alt"}))
    return _block((out / "index.html").read_text(encoding="utf-8"))


# --- :focus-visible, not :focus-within ---------------------------------

def test_focus_visible_present_on_label_swappable_rule(swap_block: str):
    # Template L339-342: hover/focus-visible hides the default.
    assert re.search(r":focus-visible\s+\.label-swappable", swap_block), \
        "no :focus-visible .label-swappable rule found"


def test_focus_visible_present_on_label_alt_rule(swap_block: str):
    # Template L343-346: hover/focus-visible shows the alt.
    assert re.search(r":focus-visible\s+\.label-alt", swap_block), \
        "no :focus-visible .label-alt rule found"



def test_focus_within_absent_from_rendered_html(swap_block: str):
    # The latching pseudo-class must not survive anywhere in the output.
    assert "focus-within" not in swap_block, \
        "found :focus-within in rendered HTML (the latching bug)"


# --- Transitions -------------------------------------------------------

def test_label_alt_has_opacity_transition(swap_block: str):
    # Template L331-334.
    m = re.search(r"\.label-alt\s*\{[^}]*transition:\s*opacity\s+1s\s+ease",
                  swap_block)
    assert m, f"no 'transition: opacity 1s ease' on .label-alt:\n{swap_block[:600]}"


def test_label_swappable_has_opacity_transition(swap_block: str):
    # Template L336-337.
    m = re.search(r"\.label-swappable\s*\{[^}]*transition:\s*opacity\s+1s\s+ease",
                  swap_block)
    assert m, f"no 'transition: opacity 1s ease' on .label-swappable:\n{swap_block[:600]}"


# --- tabindex ----------------------------------------------------------

def test_inner_div_has_tabindex_zero(swap_block: str):
    # Without tabindex="0" the div can't receive keyboard focus, and
    # :focus-visible can never fire — the swap would be keyboard-dead.
    assert re.search(r'tabindex="0"', swap_block), \
        "no tabindex=\"0\" on the diagram div"


def test_inner_div_has_role_img(swap_block: str):
    # role="img" exposes the diagram as a single image to AT.
    assert re.search(r'role="img"', swap_block), \
        "no role=\"img\" on the diagram div"


def test_inner_div_has_aria_label(swap_block: str):
    # The accessible name comes from aria-label (title + desc), not from
    # the (now-gone) SVG <title>/<desc> + aria-labelledby.
    assert re.search(r'aria-label="[^"]+"', swap_block), \
        "no aria-label on the diagram div"
