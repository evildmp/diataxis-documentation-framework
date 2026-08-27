"""Per-instance CSS scoping: every selector is namespaced to its diagram id.

An inline ``<style>`` applies document-wide, so when several diagrams appear
on one page the last diagram's rules would clobber every earlier one's
(last-declaration-wins at equal specificity). The extension mints a
monotonic ``diagram_id`` per instance and prefixes **every** selector with
``#<diagram_id>``, and namespaces the ``@keyframes`` name too.

These tests pin:

* two diagrams on one page get distinct ``id`` attributes;
* the scoped ``<style>`` block contains no surviving Jinja2 placeholders
  (``{{`` / ``}}``);
* every selector in the block is prefixed with the diagram's ``#id``
  (no bare ``.class`` rules that would leak document-wide);
* the ``@keyframes`` name is namespaced to the diagram id.
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


def _two_diagram_rst() -> str:
    """Two diagrams on one page (one with an -alt, so its cue keyframes
    exist; one without, so they don't collide)."""
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


def _style_block(block: str) -> str:
    m = re.search(r"<style>(.*?)</style>", block, re.DOTALL)
    assert m, f"no <style> block found:\n{block[:300]}"
    return m.group(1)


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


# --- All selectors prefixed with #id -----------------------------------

def test_every_selector_is_scoped_to_diagram_id(tmp_path: Path):
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    for block in blocks:
        did = _diagram_id(block)
        style = _style_block(block)
        # Find every rule (selector { ... }). A "rule" here is a line that
        # ends with { and is not a property declaration (those end with ;).
        # We check that each selector line either starts with #id or is a
        # continuation/nested rule (keyframes percentages, etc.).
        for line in style.split("\n"):
            stripped = line.strip()
            # Skip blank lines, comments, declarations (end with ;), and
            # closing braces.
            if not stripped or stripped.startswith("/*") or stripped.endswith(";") \
                    or stripped == "}" or stripped.startswith("0%") \
                    or stripped.startswith("50%") or stripped.startswith("100%") \
                    or stripped.endswith("}") and "{" not in stripped:
                continue
            # Any line opening a rule block must reference the diagram id.
            if "{" in stripped:
                assert did in stripped, \
                    f"unscoped rule in {did}:\n{stripped}\n---\n{style[:400]}"


def test_no_bare_class_selectors_leak(tmp_path: Path):
    """No rule selector should be a bare ``.class`` (without a #id prefix).

    A bare ``.type { ... }`` would apply to every diagram on the page. The
    extension scopes every selector to ``#<diagram_id>``, so a line like
    ``.type {`` (with no preceding ``#``) must not appear.
    """
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    for block in blocks:
        style = _style_block(block)
        # A bare class selector opening a rule would be a line like
        # ".type {" with no "#" on that line. Property declarations also
        # contain no "{", so filter to rule-opening lines only.
        for line in style.split("\n"):
            stripped = line.strip()
            if "{" not in stripped:
                continue
            # Skip @keyframes (it's namespaced, tested below) and its
            # percentage rules.
            if stripped.startswith("@") or stripped[0].isdigit() \
                    or stripped.endswith("%"):
                continue
            assert "#" in stripped, \
                f"bare (unscoped) selector rule:\n{stripped}"


# --- @keyframes namespacing --------------------------------------------

def test_keyframes_namespaced_per_instance(tmp_path: Path):
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    # Only the first diagram has -alt labels, so only it emits keyframes.
    block_with_cue = blocks[0]
    did = _diagram_id(block_with_cue)
    style = _style_block(block_with_cue)
    assert f"@keyframes {did}-cue-pulse" in style, \
        f"no @keyframes {did}-cue-pulse:\n{style[:400]}"
    # The animation property must reference the namespaced name.
    assert f"animation: {did}-cue-pulse" in style, style


def test_no_bare_keyframes_name(tmp_path: Path):
    """No un-namespaced ``@keyframes cue-pulse`` (would collide across
    diagrams)."""
    out = _build_html(tmp_path, _two_diagram_rst())
    blocks = _diagram_blocks((out / "index.html").read_text(encoding="utf-8"))
    for block in blocks:
        style = _style_block(block)
        # A bare "cue-pulse" (without a diagram-id prefix) would collide.
        bare = re.search(r"@keyframes\s+(?!diataxis-diagram-\d+-)cue-pulse",
                         style)
        assert bare is None, f"un-namespaced @keyframes found:\n{bare.group(0)}"
