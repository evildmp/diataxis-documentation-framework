"""Test that no Jinja2 placeholder survives in the inlined SVG.

The SVG template (``extensions/diataxis_diagram/diataxis-diagram-template.svg``)
is rendered with Jinja2 (autoescape on). Jinja2 is whitespace-insensitive
around variable names, so ``{{name}}``, ``{{ name}}`` and ``{{ name }}`` all
resolve to the same variable — this is native to the templating engine and
needs no custom handling in the extension.

These tests remain as a regression guard: they scan the full inlined SVG
(not just the ``<style>`` block) for any surviving ``{{`` / ``}}`` and assert
that every variable resolves to its configured value.
"""

from __future__ import annotations

import importlib.util as _il
import re
from pathlib import Path

from sphinx.application import Sphinx

# Load the shared fixtures from the sibling conftest.py by path.
_spec = _il.spec_from_file_location(
    "_diataxis_diagram_conftest",
    Path(__file__).resolve().parent / "conftest.py",
)
assert _spec is not None and _spec.loader is not None
_mod = _il.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
LABEL_VALUES = _mod.LABEL_VALUES
TITLE_TEXT = _mod.TITLE_TEXT
DESC_TEXT = _mod.DESC_TEXT
_ensure_extensions_importable = _mod._ensure_extensions_importable


# A template that exercises every variable the extension injects, in mixed
# whitespace forms (no-space, half-space, fully-spaced). Jinja2 resolves all
# three forms to the same variable; the test asserts none survive and that the
# configured values land in the right attributes.
_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <style>
      .axis { font-size: {{axis_font_size}}px; }
      .type { font-size: {{ type_font_size}}px; }
      .purpose { font-size: {{purpose_font_size }}px; }
    </style>
  </defs>
  <line x1="0" y1="0" x2="100" y2="0" stroke="black"/>
  <text id="dimension-theory" class="axis" x="0" y="-{{axis_y}}" {% if y_axis_mode == "rotated" %}text-anchor="start" transform="rotate(-90 0 -{{ axis_y }})"{% else %}text-anchor="end" writing-mode="vertical-rl"{% endif %}>{{ dimension_theory }}</text>
  <text id="dimension-action" class="axis" x="0" y="{{ axis_y}}" {% if y_axis_mode == "rotated" %}text-anchor="end" transform="rotate(-90 0 {{ axis_y }})"{% else %}text-anchor="start" writing-mode="vertical-rl"{% endif %}>{{ dimension_action }}</text>
  <text id="tutorials" class="type" x="-10" y="-{{type_y}}">{{ tutorials }}</text>
  <text id="explanation" class="type" x="-10" y="{{ type_y}}">{{ explanation }}</text>
  <text id="orientation-tutorial" class="purpose" x="-{{type_purpose_x}}" y="-{{ purpose_y}}">{{ orientation_tutorial }}</text>
  <text id="orientation-explanation" class="purpose" x="-{{ type_purpose_x }}" y="{{purpose_y}}">{{ orientation_explanation }}</text>
  <text id="relation-development" class="axis" x="-{{axis_x}}" y="0">{{ relation_development }}</text>
  <text id="how-to" class="type" x="10" y="-{{type_y}}">{{ how_to }}</text>
  <text id="reference" class="type" x="10" y="{{type_y}}">{{ reference }}</text>
  <text id="orientation-how-to" class="purpose" x="{{type_purpose_x}}" y="-{{purpose_y}}">{{ orientation_how_to }}</text>
  <text id="orientation-reference" class="purpose" x="{{ type_purpose_x }}" y="{{purpose_y}}">{{ orientation_reference }}</text>
  <text id="relation-application" class="axis" x="{{axis_x}}" y="0">{{ relation_application }}</text>
  {% if guides %}
  <line x1="-{{type_purpose_x}}" y1="-50" x2="-{{type_purpose_x}}" y2="50" stroke="#999" stroke-width="1"/>
  {% endif %}
</svg>
"""


_CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Daniele Procida"
language = {language!r}
master_doc = "index"
exclude_patterns = []
diataxis_diagram = {typography!r}
"""


def _index_rst() -> str:
    label_lines = "\n   ".join(
        f':{name}: "{value}"' for name, value in LABEL_VALUES.items()
    )
    return (
        "Welcome\n"
        "=======\n"
        "\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f"   {label_lines}\n"
    )


def _build_with_template(tmp_path: Path, template: str, typography: dict) -> Path:
    """Build a Sphinx project whose extension uses ``template`` as the SVG.

    The extension loads its template from
    ``Path(__file__).parent / "diataxis-diagram-template.svg"`` at visit time,
    so we monkeypatch that file on disk for the duration of the build.
    """
    _ensure_extensions_importable()
    ext_dir = Path(__file__).resolve().parents[1]
    real_template = ext_dir / "diataxis-diagram-template.svg"
    backup = ext_dir / "diataxis-diagram-template.svg.bak"

    real_template.rename(backup)
    try:
        real_template.write_text(template, encoding="utf-8")

        src = tmp_path / "src"
        out = tmp_path / "out"
        doctree = tmp_path / "doctrees"
        src.mkdir()
        (src / "conf.py").write_text(
            _CONF_PY.format(language="en", typography=typography),
            encoding="utf-8",
        )
        (src / "index.rst").write_text(_index_rst(), encoding="utf-8")

        app = Sphinx(
            srcdir=str(src),
            confdir=str(src),
            outdir=str(out),
            doctreedir=str(doctree),
            buildername="html",
            freshenv=True,
        )
        app.build()
        return out
    finally:
        real_template.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
        backup.unlink()


def _inlined_svg(html: str) -> str:
    """Return the full inlined ``<svg>...</svg>`` block from the HTML."""
    m = re.search(r'(<svg[^>]*>.*?</svg>)', html, re.DOTALL)
    assert m is not None, "no <svg> block found in HTML"
    return m.group(1)


def test_no_placeholder_survives_anywhere_in_inlined_svg(tmp_path: Path):
    """No ``{{`` or ``}}`` may survive anywhere in the inlined SVG — not just
    in the ``<style>`` block. The template above mixes no-space and half-space
    variable forms; Jinja2 must resolve all of them."""
    typography = {
        "en": {
            "font-sizes": {"type": 104, "purpose": 44, "axis": 44},
            "offsets": {
                "axis-x": 154,
                "type-purpose-x": 154,
                "axis-y": 119,
                "purpose-y": 119,
                "type-y": 240,
            },
            "y-axis-rotation": "rotated",
            "guides": True,
        },
    }
    out = _build_with_template(tmp_path, _TEMPLATE, typography)
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))
    assert "{{" not in svg, f"unsubstituted placeholder in SVG:\n{svg}"
    assert "}}" not in svg, f"unsubstituted placeholder in SVG:\n{svg}"


def test_whitespace_variants_of_same_key_substitute_identically(tmp_path: Path):
    """``{{name}}``, ``{{ name}}`` and ``{{ name }}`` must all resolve to the
    same variable. The template above puts ``{{y_axis}}`` (no spaces)
    on one element and ``{{ y_axis}}`` (half-spaced) on another; both
    must become the configured ``y-axis`` value (119)."""
    typography = {
        "en": {
            "font-sizes": {"type": 104, "purpose": 44, "axis": 44},
            "offsets": {
                "axis-x": 154,
                "type-purpose-x": 154,
                "axis-y": 119,
                "purpose-y": 119,
                "type-y": 240,
            },
            "y-axis-rotation": "rotated",
            "guides": False,
        },
    }
    out = _build_with_template(tmp_path, _TEMPLATE, typography)
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))
    # The dimension-theory label sits at y=-119 (top), dimension-action at y=119 (bottom).
    # Both use no-space or half-space forms in the template.
    assert 'y="-119"' in svg, svg
    assert 'y="119"' in svg, svg
    # y-type (240) appears on the four type labels, all no-space
    # or half-space forms in the template.
    assert 'y="-240"' in svg, svg
    assert 'y="240"' in svg, svg
    # x-type-purpose (154) appears in several forms; all must resolve.
    assert 'x="-154"' in svg, svg
    assert 'x="154"' in svg, svg
    # Font sizes substituted into the <style> block.
    assert "font-size: 104px" in svg, svg
    assert "font-size: 44px" in svg, svg


def test_real_template_leaves_no_placeholders(tmp_path: Path):
    """The shipped template (``diataxis-diagram-template.svg``) must also
    leave no ``{{`` / ``}}`` anywhere in the inlined SVG. This is the
    regression guard for the actual file, not just the synthetic one."""
    typography = {
        "en": {
            "font-sizes": {"type": 104, "purpose": 44, "axis": 44},
            "offsets": {
                "axis-x": 154,
                "type-purpose-x": 154,
                "axis-y": 119,
                "purpose-y": 119,
                "type-y": 240,
            },
            "y-axis-rotation": "rotated",
            "guides": False,
        },
    }
    real_template = (
        Path(__file__).resolve().parents[1]
        / "diataxis-diagram-template.svg"
    ).read_text(encoding="utf-8")
    out = _build_with_template(tmp_path, real_template, typography)
    svg = _inlined_svg((out / "index.html").read_text(encoding="utf-8"))
    assert "{{" not in svg, f"unsubstituted placeholder in shipped SVG:\n{svg}"
    assert "}}" not in svg, f"unsubstituted placeholder in shipped SVG:\n{svg}"
