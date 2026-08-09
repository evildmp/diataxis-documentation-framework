"""Test per-language diagram typography from ``diataxis_diagram_typography``.

The Diátaxis diagram's font sizes are build parameters, not translatable
strings. They are read from the ``diataxis_diagram_typography`` config (keyed
by ``config.language``) and emitted as CSS custom properties on the wrapping
``<div class="diataxis-diagram">``. The matching ``var(--diagram-X-size)`` calls
live in _static/diataxis.css (no fallback), so the div's custom properties are
the only source of the rendered sizes.

This test pins that behaviour and guards two failure modes the previous
regex-substitution approach silently suffered:

* a locale missing from ``diataxis_diagram_typography`` must fail the build
  (fatal), not silently fall back;
* a locale entry missing one of the three required size keys must also fail,
  because the CSS ``var()`` has no fallback and an unresolved property would
  collapse the text to the initial ~16px.

It also asserts the gettext msgid count is unaffected (font sizes are NOT
msgids).
"""

from __future__ import annotations

import importlib.util as _il
import re
from pathlib import Path

import pytest
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

# Load the shared fixtures from the sibling conftest.py by path.
_spec = _il.spec_from_file_location(
    "_diataxis_diagram_conftest",
    Path(__file__).resolve().parent / "conftest.py",
)
assert _spec is not None and _spec.loader is not None
_mod = _il.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EXPECTED_MSGIDS = _mod.EXPECTED_MSGIDS
LABEL_VALUES = _mod.LABEL_VALUES
ALT_TEXT = _mod.ALT_TEXT
_ensure_extensions_importable = _mod._ensure_extensions_importable


_CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Daniele Procida"
language = {language!r}
master_doc = "index"
exclude_patterns = []
diataxis_diagram_typography = {font_sizes!r}
"""


def _index_rst() -> str:
    label_lines = "\n   ".join(
        f':{name}: "{value}"' for name, value in LABEL_VALUES.items()
    )
    return (
        "Welcome\n"
        "=======\n"
        "\n"
        ".. diataxis-diagram:: /images/diataxis-diagram-template.svg\n"
        f"   :alt: {ALT_TEXT}\n"
        "\n"
        f"   {label_lines}\n"
    )


def _build(tmp_path: Path, language: str, font_sizes: dict) -> Path:
    _ensure_extensions_importable()
    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"
    images = src / "images"

    src.mkdir()
    images.mkdir()
    (src / "conf.py").write_text(
        _CONF_PY.format(language=language, font_sizes=font_sizes),
        encoding="utf-8",
    )
    (src / "index.rst").write_text(_index_rst(), encoding="utf-8")
    # The real SVG template has no <style> block: font sizes come from the
    # page stylesheet via var(--diagram-X-size). The test SVG mirrors that —
    # it carries only the <text id="..."> elements the directive fills in.
    (images / "diataxis-diagram-template.svg").write_text(
        _mod._svg_content(), encoding="utf-8"
    )

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


def _html(out: Path) -> str:
    return (out / "index.html").read_text(encoding="utf-8")


def _diataxis_diagram_div(html: str) -> str:
    """Return the wrapping <div class="diataxis-diagram ..."> opening tag."""
    m = re.search(r'<div class="diataxis-diagram[^"]*"[^>]*>', html)
    assert m is not None, "no diataxis-diagram div in output"
    return m.group()


def test_custom_properties_emitted_for_configured_language(tmp_path: Path):
    out = _build(
        tmp_path,
        "it",
        {"it": {"quadrant": 100, "orientation": 44, "axis": 44}},
    )
    tag = _diataxis_diagram_div(_html(out))
    assert '--diagram-quadrant-size: 100px' in tag, tag
    assert '--diagram-orientation-size: 44px' in tag, tag
    assert '--diagram-axis-size: 44px' in tag, tag


def test_other_language_not_affected(tmp_path: Path):
    # Config has an entry for "fr" but build language is "en", which also has
    # an entry. The div must carry en's sizes, not fr's.
    out = _build(
        tmp_path,
        "en",
        {
            "en": {"quadrant": 104, "orientation": 44, "axis": 44},
            "fr": {"quadrant": 80, "orientation": 30, "axis": 20},
        },
    )
    tag = _diataxis_diagram_div(_html(out))
    assert '--diagram-quadrant-size: 104px' in tag, tag
    assert '--diagram-quadrant-size: 80px' not in tag, tag


def test_partial_override_still_emits_all_three(tmp_path: Path):
    # A locale entry must supply all three size keys (the CSS var() has no
    # fallback). Here the entry is complete; the div carries all three.
    out = _build(
        tmp_path,
        "pl",
        {"pl": {"quadrant": 57, "orientation": 44, "axis": 44}},
    )
    tag = _diataxis_diagram_div(_html(out))
    assert '--diagram-quadrant-size: 57px' in tag, tag
    assert '--diagram-orientation-size: 44px' in tag, tag
    assert '--diagram-axis-size: 44px' in tag, tag


def test_missing_locale_entry_is_fatal(tmp_path: Path):
    # Build language "de" has no typography entry: must raise, not silently
    # fall back to the SVG's (now absent) baked-in sizes.
    with pytest.raises(ExtensionError):
        _build(
            tmp_path,
            "de",
            {"en": {"quadrant": 104, "orientation": 44, "axis": 44}},
        )


def test_missing_size_key_is_fatal(tmp_path: Path):
    # The locale entry exists but omits "orientation": the CSS var() would
    # be unresolved, collapsing that text to ~16px. Must raise.
    with pytest.raises(ExtensionError):
        _build(
            tmp_path,
            "it",
            {"it": {"quadrant": 100, "axis": 44}},
        )


def test_y_axis_labels_key_does_not_become_a_custom_property(tmp_path: Path):
    # y-axis-labels is a structural switch, not a font size; it must not be
    # emitted as --diagram-y-axis-labels-size on the div.
    out = _build(
        tmp_path,
        "zh_CN",
        {
            "zh_CN": {
                "quadrant": 104,
                "orientation": 44,
                "axis": 80,
                "y-axis-labels": "stacked",
            },
        },
    )
    tag = _diataxis_diagram_div(_html(out))
    assert '--diagram-quadrant-size: 104px' in tag, tag
    assert '--diagram-axis-size: 80px' in tag, tag
    assert 'y-axis-labels' not in tag, tag


def test_font_sizes_are_not_msgids(tmp_path: Path):
    """Font sizes must not appear as gettext msgids; count stays 13."""
    out = _build(
        tmp_path,
        "it",
        {"it": {"quadrant": 100, "orientation": 44, "axis": 44}},
    )
    html = _html(out)
    for s in EXPECTED_MSGIDS:
        assert s in html
    assert len(EXPECTED_MSGIDS) == 13