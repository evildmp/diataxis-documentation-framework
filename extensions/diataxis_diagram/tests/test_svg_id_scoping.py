"""Tests for per-instance SVG id scoping of ``.. diataxis-diagram::``.

When several diagrams appear on one HTML page, each inline SVG carries its own
``<style>`` block. An ``<svg>``'s ``<style>`` is **not** scoped to that SVG —
it applies document-wide — so without per-instance ids the last diagram's
rules would clobber every earlier one's (last-declaration-wins at equal
specificity), and fixed filter ids would collide.

Each instance therefore mints a unique ``svg_id`` and derives ``title`` /
``desc`` / filter ids from it; every CSS selector is scoped to
``#{{ svg_id }}`` (``.annotation`` becomes ``#{{ svg_id }} .annotation text``
so ``font-size`` lands on each ``<text>`` for ``em`` resolution), and every
``id`` and ``url(#...)`` ref is namespaced to the instance.

These tests render two diagrams on one page — one with a 1-line annotation
block (font size ~100px) and one with a 5-line block (~56px) — and assert the
two instances don't interfere.
"""

from __future__ import annotations

import importlib.util as _il
import re
from pathlib import Path

from sphinx.application import Sphinx

# Load shared fixtures from the sibling conftest.py by path.
_spec = _il.spec_from_file_location(
    "_diataxis_diagram_conftest_scoping",
    Path(__file__).resolve().parent / "conftest.py",
)
assert _spec is not None and _spec.loader is not None
_mod = _il.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
TITLE_TEXT = _mod.TITLE_TEXT
DESC_TEXT = _mod.DESC_TEXT
_ensure_extensions_importable = _mod._ensure_extensions_importable


_CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Daniele Procida"
language = "en"
master_doc = "index"
exclude_patterns = []
diataxis_diagram = {{"en": {{"font-sizes": {{"axis": 42}}}}}}
"""


def _index_rst_with_two_diagrams() -> str:
    """A page with two ``.. diataxis-diagram::`` directives.

    The first has a single-line ``:top-half:`` block; the second has a
    five-line ``:top-half:`` block. The two must end up with different
    annotation font sizes and not clobber each other.
    """
    return (
        "Welcome\n"
        "=======\n"
        "\n"
        "..  diataxis-diagram::\n"
        "   :title: One\n"
        "   :desc: First diagram\n"
        "\n"
        '   :top-half: "solo"\n'
        '   :axis-label-bottom: "Practical capacity"\n'
        "\n"
        "..  diataxis-diagram::\n"
        "   :title: Two\n"
        "   :desc: Second diagram\n"
        "\n"
        '   :top-half: "a", "b", "c", "d", "e"\n'
        '   :axis-label-bottom: "Practical capacity"\n'
    )


def _build_page(tmp_path: Path) -> str:
    _ensure_extensions_importable()
    rst = _index_rst_with_two_diagrams()

    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"
    src.mkdir()
    (src / "conf.py").write_text(_CONF_PY.format(), encoding="utf-8")
    (src / "index.rst").write_text(rst, encoding="utf-8")

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(doctree),
        buildername="html",
        freshenv=True,
    )
    app.build()
    return (out / "index.html").read_text(encoding="utf-8")


def _all_svgs(html: str) -> list[str]:
    """Return every ``<svg ...>...</svg>`` block in *html*, in document order."""
    return re.findall(r"(<svg[^>]*>.*?</svg>)", html, re.DOTALL)


def _svg_id(svg: str) -> str:
    m = re.search(r'<svg[^>]*\bid="([^"]+)"', svg)
    assert m is not None, "svg has no id"
    return m.group(1)


def _style_block(svg: str) -> str:
    m = re.search(r"<style>(.*?)</style>", svg, re.DOTALL)
    assert m is not None, "svg has no <style> block"
    return m.group(1)


def _annotation_font_size_px(style: str) -> float:
    m = re.search(
        r"#\S+\s+\.annotation text\s*\{[^}]*font-size:\s*([0-9.]+)px",
        style,
        re.DOTALL,
    )
    assert m is not None, f"no .annotation text font-size in style:\n{style}"
    return float(m.group(1))


# ---------------------------------------------------------------------------
# Per-instance uniqueness
# ---------------------------------------------------------------------------


def test_each_svg_has_a_distinct_id(tmp_path):
    html = _build_page(tmp_path)
    svgs = _all_svgs(html)
    assert len(svgs) == 2, f"expected 2 SVGs, got {len(svgs)}"
    ids = [_svg_id(s) for s in svgs]
    assert ids[0] != ids[1], f"both SVGs share id {ids[0]!r}"
    assert all(i.startswith("diataxis-diagram-") for i in ids), ids


def test_aria_labelledby_references_own_title_and_desc_ids(tmp_path):
    html = _build_page(tmp_path)
    for svg in _all_svgs(html):
        sid = _svg_id(svg)
        m = re.search(r'aria-labelledby="([^"]+)"', svg)
        assert m is not None, "svg has no aria-labelledby"
        title_id, desc_id = m.group(1).split()
        assert title_id == f"{sid}-title", (sid, title_id)
        assert desc_id == f"{sid}-desc", (sid, desc_id)
        assert f'id="{title_id}"' in svg
        assert f'id="{desc_id}"' in svg


def test_filter_id_and_refs_are_namespaced_to_instance(tmp_path):
    html = _build_page(tmp_path)
    for svg in _all_svgs(html):
        sid = _svg_id(svg)
        expected_filter = f"{sid}-label-bg"
        assert f'id="{expected_filter}"' in svg, (
            f"filter id not namespaced: expected {expected_filter!r}"
        )
        # Every url(#...) ref must point at this instance's filter, never the
        # old shared "label-bg".
        refs = re.findall(r'url\(#([^)]+)\)', svg)
        assert refs, "no filter url(#...) refs in svg"
        assert all(r == expected_filter for r in refs), refs
        assert 'url(#label-bg)' not in svg  # no bare shared ref left


def test_annotation_font_size_differs_per_instance(tmp_path):
    """The 1-line block sizes to ~100px; the 5-line block to ~56px. They must
    not be equal (the whole point of scoping the <style>)."""
    html = _build_page(tmp_path)
    svgs = _all_svgs(html)
    sizes = [_annotation_font_size_px(_style_block(s)) for s in svgs]
    assert sizes[0] != sizes[1], f"both instances share font size {sizes}"
    # Solo (n=1) -> ~100; five lines (n=5) -> ~56.
    assert sizes[0] == 100.0, sizes  # n=1: 100 / (1 + 0.10 * 0**1.5) = 100.0
    assert sizes[1] < 60.0, sizes   # n=5: 100 / (1 + 0.10 * 4**1.5) ≈ 56.0


def test_each_style_block_is_scoped_to_its_own_svg_id(tmp_path):
    """Every selector in an instance's <style> must be anchored to that
    instance's ``#svg_id``, so the two stylesheets don't match each other's
    elements."""
    html = _build_page(tmp_path)
    for svg in _all_svgs(html):
        sid = _svg_id(svg)
        style = _style_block(svg)
        # No selector may use the unscoped, document-wide form.
        assert ".diataxis-diagram ." not in style, (
            f"unscoped .diataxis-diagram selector left in {sid}:\n{style}"
        )
        # The annotation rule targets <text> directly (fixes em-resolution).
        assert f"#{sid} .annotation text" in style, style
        for cls in (".axis", ".type", ".purpose"):
            assert f"#{sid} {cls}" in style, (cls, style)


def test_no_bare_shared_ids_survive(tmp_path):
    """No functional id should keep a bare, instance-agnostic form that could
    collide across diagrams (title/desc/filter were the functional ones).
    Label element ids are intentionally left bare and may duplicate across
    instances; they are never referenced functionally."""
    html = _build_page(tmp_path)
    bare = [
        name
        for name in (
            'id="diagram-map-title"',
            'id="diagram-map-description"',
            'id="label-bg"',
            'url(#label-bg)',
        )
        if name in html
    ]
    assert not bare, f"bare (un-namespaced) functional ids survived: {bare}"


def test_no_placeholder_survives(tmp_path):
    html = _build_page(tmp_path)
    for svg in _all_svgs(html):
        assert "{{" not in svg, f"unsubstituted placeholder in SVG:\n{svg}"
        assert "}}" not in svg, f"unsubstituted placeholder in SVG:\n{svg}"
