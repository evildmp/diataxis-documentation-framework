"""CSS typography and structural CSS pinned in the shared stylesheet.

These tests pin the typography and stroke-floor decisions that the HTML/CSS
rewrite relies on, so a future edit can't silently undo them:

* ``text-box-edge: cap alphabetic`` + ``text-box-trim: trim-both`` on the
  uppercase ``.type`` and ``.purpose`` classes only (NOT on ``.axis`` /
  ``.need`` — descenders affect the top slots, not the bottom ones);
* ``line-height: 1`` reset on the diagram container (the page's ``article``
  sets 1.5, which was bleeding into the diagram and pushing purpose labels
  off their guide lines);
* ``max(...cqw, 1px)`` px floors on the axis and guide strokes (so they
  stay visible at small container sizes / in sidebar variants);
* font sizes expressed as CSS custom properties in ``cqw`` units (not
  ``px``), consumed via ``var(--type-font)`` etc.
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

# All diagram CSS now lives in the extension's shared stylesheet.
CSS = shared_css()


@pytest.fixture
def block(tmp_path: Path) -> str:
    out = _build_html(tmp_path, (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        '   :name-top-left: "T"\n'
    ))
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    assert len(blocks) == 1
    return blocks[0]


def _rule(block: str, selector_suffix: str) -> str | None:
    """Return the first CSS rule body matching a selector ending in suffix.

    Selectors are scoped to ``#<diagram_id>`` and may span multiple lines;
    this helper finds a declaration block whose selector contains the suffix
    and returns its body (the text between ``{`` and ``}``).
    """
    # Match: selector(s) ending in suffix, then { declarations }
    pattern = re.compile(
        r"((?:#[^\s{}]+\s+)*" + re.escape(selector_suffix) + r")\s*\{([^}]*)\}",
        re.DOTALL,
    )
    m = pattern.search(block)
    return m.group(2) if m else None


# --- text-box-trim (uppercase classes only) ----------------------------

def test_type_has_text_box_edge_and_trim():
    body = _rule(CSS, ".type")
    assert body is not None, "no .type rule found"
    assert "text-box-edge: cap alphabetic" in body, body
    assert "text-box-trim: trim-both" in body, body


def test_purpose_has_text_box_edge_and_trim():
    body = _rule(CSS, ".purpose")
    assert body is not None, "no .purpose rule found"
    assert "text-box-edge: cap alphabetic" in body, body
    assert "text-box-trim: trim-both" in body, body


def test_axis_does_not_have_text_box_trim():
    body = _rule(CSS, ".axis")
    assert body is not None, "no .axis rule found"
    assert "text-box-trim" not in body, body
    assert "text-box-edge" not in body, body


def test_need_does_not_have_text_box_trim():
    body = _rule(CSS, ".need")
    assert body is not None, "no .need rule found"
    assert "text-box-trim" not in body, body
    assert "text-box-edge" not in body, body


def test_type_and_purpose_are_uppercase():
    for cls in (".type", ".purpose"):
        body = _rule(CSS, cls)
        assert body is not None, f"no {cls} rule found"
        assert "text-transform: uppercase" in body, (cls, body)


# --- line-height reset -------------------------------------------------

def test_diagram_container_has_line_height_one():
    # The container rule is .diataxis-diagram .diagram-root { ... }.
    m = re.search(r"\.diataxis-diagram \.diagram-root\s*\{([^}]*)\}", CSS,
                  re.DOTALL)
    assert m, "no .diagram-root container rule found"
    assert "line-height: 1" in m.group(1), m.group(1)


# --- Stroke floors (max(...cqw, 1px)) -----------------------------------

def test_axis_stroke_has_px_floor(block: str):
    # Inline style var: --axis-stroke: max(...cqw, 1px)
    m = re.search(r"--axis-stroke:\s*max\([^,]+cqw,\s*1px\)", block)
    assert m, f"no --axis-stroke max(...,1px) floor:\n{block[:500]}"


def test_guide_stroke_has_px_floor(block: str):
    m = re.search(r"--guide-stroke:\s*max\([^,]+cqw,\s*1px\)", block)
    assert m, f"no --guide-stroke max(...,1px) floor:\n{block[:500]}"


# --- Font sizes as cqw CSS variables -----------------------------------

@pytest.mark.parametrize(
    "var_name",
    ["--type-font", "--purpose-font", "--axis-font", "--need-font",
     "--annotation-font"],
)
def test_font_size_var_is_cqw(block: str, var_name: str):
    m = re.search(rf"{re.escape(var_name)}:\s*[\d.]+cqw", block)
    assert m, f"{var_name} not a cqw value:\n{block[:500]}"


def test_font_size_consumed_via_var():
    # The shared stylesheet must reference the CSS vars (not hardcode px).
    for var in ("--type-font", "--purpose-font", "--axis-font"):
        assert f"font-size: var({var})" in CSS, \
            f"no 'font-size: var({var})' in stylesheet:\n{CSS[:500]}"
