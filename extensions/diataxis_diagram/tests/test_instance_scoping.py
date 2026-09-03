"""Shared-stylesheet architecture: no per-instance CSS, instance-scoped vars.

Styling lives in one shared stylesheet, ``static/diataxis-diagram.css``,
registered by ``setup()`` and scoped under the ``.diataxis-diagram`` class.
Per-instance variation comes from CSS custom properties set inline on each
diagram's ``.diagram-root`` element; the instance id is still minted and
carried on the root ``<div>`` but never appears in selectors.

These tests pin:

* two diagrams on one page get distinct ``id`` attributes;
* rendered diagram blocks contain no surviving Jinja2 placeholders
  (``{{`` / ``}}``);
* no per-instance ``<style>`` block is emitted;
* each diagram's custom properties are instance-scoped via the inline
  ``style`` attribute on its ``.diagram-root`` element;
* the shared stylesheet has no instance-specific selectors (no ``#id``)
  and one shared ``@keyframes`` name.
"""

from __future__ import annotations

import importlib.util as _il
import re
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

EXTENSION_DIR = Path(__file__).resolve().parent.parent
SHARED_CSS = EXTENSION_DIR / "static" / "diataxis-diagram.css"


def _two_diagram_rst() -> str:
    """Two diagrams on one page (one with an -alt, exercising the swap)."""
    return (
        "Welcome\n=======\n\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        '   :name-top-left: "First"\n'
        '   :name-top-left-alt: "First alt"\n'
        "\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT} 2\n"
        f"   :desc: {DESC_TEXT} 2\n"
        "\n"
        '   :name-top-left: "Second"\n'
    )


def _diagram_id(block: str) -> str:
    m = re.search(r'<div id="(diataxis-diagram-\d+)"', block)
    assert m, f"no diagram id found:\n{block[:200]}"
    return m.group(1)


# --- Distinct ids ------------------------------------------------------

def test_two_diagrams_get_distinct_ids(tmp_path: Path):
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    assert len(blocks) == 2, f"expected 2 diagrams, got {len(blocks)}"
    ids = [_diagram_id(b) for b in blocks]
    assert ids[0] != ids[1], f"diagram ids collide: {ids}"
    # Ids follow the expected pattern.
    for did in ids:
        assert re.match(r"diataxis-diagram-\d+", did), did


# --- No surviving Jinja2 placeholders ----------------------------------

def test_no_placeholders_survive_in_single_diagram(tmp_path: Path):
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    for i, block in enumerate(blocks):
        assert "{{" not in block, f"diagram {i} has surviving '{{'"
        assert "}}" not in block, f"diagram {i} has surviving '}}'"


# --- No per-instance <style> block -------------------------------------

def test_no_per_instance_style_block(tmp_path: Path):
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    for i, block in enumerate(blocks):
        assert "<style" not in block, \
            f"diagram {i} emits a per-instance <style> block:\n{block[:300]}"


# --- Custom properties instance-scoped via inline style ----------------

def test_custom_properties_are_instance_scoped(tmp_path: Path):
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    for i, block in enumerate(blocks):
        did = _diagram_id(block)
        # The root div carries the id, the diagram-root class, and the
        # instance's custom properties in one inline style attribute.
        root = re.search(
            r'<div id="' + did + r'" class="[^"]*diagram-root[^"]*"[^>]*>',
            block,
        )
        assert root, f"diagram {i}: no .diagram-root div for {did}"
        assert "style=" in root.group(0), \
            f"diagram {i}: custom properties not inline on .diagram-root"
        assert "--grid-cols" in root.group(0), \
            f"diagram {i}: expected custom properties on .diagram-root"


# --- Shared stylesheet: no instance-specific selectors -----------------

def test_shared_css_has_no_instance_selectors():
    css = SHARED_CSS.read_text(encoding="utf-8")
    # No selector may reference a per-instance id.
    assert not re.search(r"#diataxis-diagram-\d+", css), \
        "shared stylesheet references a per-instance id"
    # Every rule is scoped under .diataxis-diagram (or is @keyframes /
    # a percentage frame inside it / an @media wrapper — the rules inside
    # the media block are checked on their own lines).
    for line in css.split("\n"):
        stripped = line.strip()
        if "{" not in stripped:
            continue
        if stripped.startswith("@keyframes") or stripped.startswith("@media") \
                or stripped[0].isdigit() or stripped.endswith("%"):
            continue
        assert ".diataxis-diagram" in stripped, \
            f"unscoped rule in shared stylesheet:\n{stripped}"


def test_shared_css_has_one_shared_keyframes_name():
    css = SHARED_CSS.read_text(encoding="utf-8")
    names = re.findall(r"@keyframes\s+([\w-]+)", css)
    assert names == ["diataxis-diagram-cue-pulse"], names
    assert "animation: diataxis-diagram-cue-pulse" in css, css
