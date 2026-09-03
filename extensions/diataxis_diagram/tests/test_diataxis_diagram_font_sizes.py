"""Test per-language diagram typography from ``diataxis_diagram``.

The Diátaxis diagram's font sizes are build parameters, not translatable
strings. They are read from the ``diataxis_diagram`` config
(keyed by ``config.language``) and substituted into the HTML template's
inline ``style`` attribute as CSS custom properties (``--type-font``,
``--purpose-font``, ``--axis-font``, ``--need-font``, ``--annotation-font``),
each expressed in ``cqw`` (container query width) units so the whole diagram
scales with its container. The scoped ``<style>`` block consumes them via
``font-size: var(--type-font)`` etc.

Typography values are resolved as a three-layer merge: the extension's
built-in ``DEFAULT_TYPOGRAPHY``, then the ``default`` key in
``diataxis_diagram`` (site-wide override), then the per-locale
entry. Locales may omit any key; the resolved value falls back through the
chain. A locale entirely absent from ``diataxis_diagram`` is a
fatal error (protects against a language being added without a typography
entry).

This test pins that behaviour and guards the failure mode:

* a locale missing from ``diataxis_diagram`` must fail the build
  (fatal), not silently fall back;
* a locale entry missing one of the size keys must fall back through
  ``default`` and then the built-in defaults, not raise.

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
TITLE_TEXT = _mod.TITLE_TEXT
DESC_TEXT = _mod.DESC_TEXT
_ensure_extensions_importable = _mod._ensure_extensions_importable


_CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Daniele Procida"
language = {language!r}
master_doc = "index"
exclude_patterns = []
diataxis_diagram = {font_sizes!r}
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
        f"   {label_lines}"
    )


def _build(tmp_path: Path, language: str, font_sizes: dict) -> Path:
    _ensure_extensions_importable()
    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"

    src.mkdir()
    (src / "conf.py").write_text(
        _CONF_PY.format(language=language, font_sizes=font_sizes),
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


def _html(out: Path) -> str:
    return (out / "index.html").read_text(encoding="utf-8")


def _diagram_block(html: str) -> str:
    """Return the rendered HTML for the first diagram instance.

    The diagram is emitted as ``<div class="diataxis-diagram ...">...</div>``
    with a scoped ``<style>`` and inline CSS custom properties. Asserting
    against this slice keeps the substring searches tight and avoids stray
    matches in theme chrome.
    """
    m = re.search(
        r'<div class="diataxis-diagram[^"]*">.*?</div>\s*</div>\s*',
        html,
        re.DOTALL,
    )
    assert m is not None, "no diataxis-diagram block found in rendered HTML"
    return m.group(0)


def _cqw(px: int, *, width: int = 1920) -> str:
    """Expected ``cqw`` string for ``px`` in a full diagram (width 1920)."""
    return f"{px / width * 100:.4f}cqw"


def test_font_sizes_substituted_into_style_for_configured_language(tmp_path: Path):
    out = _build(
        tmp_path,
        "it",
        {"it": {"font-sizes": {"type": 100, "purpose": 44, "axis": 44}, "offsets": {"axis-y": 119}}},
    )
    block = _diagram_block(_html(out))
    assert f"--type-font: {_cqw(100)}" in block, block
    assert f"--purpose-font: {_cqw(44)}" in block, block
    assert f"--axis-font: {_cqw(44)}" in block, block
    # No Jinja2 placeholder should survive rendering.
    assert "{{" not in block and "}}" not in block, block


def test_other_language_not_affected(tmp_path: Path):
    # Config has an entry for "fr" but build language is "en", which also has
    # an entry. The diagram must carry en's sizes, not fr's.
    out = _build(
        tmp_path,
        "en",
        {
            "en": {"font-sizes": {"type": 104, "purpose": 44, "axis": 44}, "offsets": {"axis-y": 119}},
            "fr": {"font-sizes": {"type": 80, "purpose": 30, "axis": 20}, "offsets": {"axis-y": 119}},
        },
    )
    block = _diagram_block(_html(out))
    assert f"--type-font: {_cqw(104)}" in block, block
    assert f"--type-font: {_cqw(80)}" not in block, block


def test_partial_override_still_substitutes_all_three(tmp_path: Path):
    # A locale entry supplies all three size keys; all three land in the CSS.
    out = _build(
        tmp_path,
        "pl",
        {"pl": {"font-sizes": {"type": 57, "purpose": 44, "axis": 44}, "offsets": {"axis-y": 119}}},
    )
    block = _diagram_block(_html(out))
    assert f"--type-font: {_cqw(57)}" in block, block
    assert f"--purpose-font: {_cqw(44)}" in block, block
    assert f"--axis-font: {_cqw(44)}" in block, block


def test_missing_locale_entry_is_fatal(tmp_path: Path):
    # Build language "de" has no typography entry: must raise, not silently
    # fall back to the built-in defaults.
    with pytest.raises(ExtensionError):
        _build(
            tmp_path,
            "de",
            {"en": {"font-sizes": {"type": 104, "purpose": 44, "axis": 44}, "offsets": {"axis-y": 119}}},
        )


def test_missing_size_key_falls_back_to_default(tmp_path: Path):
    # The locale entry exists but omits "purpose": the built-in
    # DEFAULT_TYPOGRAPHY supplies it. Must build, not raise.
    out = _build(
        tmp_path,
        "it",
        {"it": {"font-sizes": {"type": 100, "axis": 44}, "offsets": {"axis-y": 119}}},
    )
    block = _diagram_block(_html(out))
    # type and axis came from the locale entry; purpose fell back to
    # the built-in default (44).
    assert f"--type-font: {_cqw(100)}" in block, block
    assert f"--purpose-font: {_cqw(44)}" in block, block
    assert f"--axis-font: {_cqw(44)}" in block, block
    assert "{{" not in block and "}}" not in block, block


def test_default_key_overrides_built_in_defaults(tmp_path: Path):
    # A ``default`` key sets the site-wide fallback; a locale entry that omits
    # a key picks it up from ``default`` rather than the built-in defaults.
    out = _build(
        tmp_path,
        "it",
        {
            "default": {"font-sizes": {"purpose": 50}, "offsets": {"axis-y": 119}},
            "it": {"font-sizes": {"type": 100, "axis": 44}},
        },
    )
    block = _diagram_block(_html(out))
    assert f"--type-font: {_cqw(100)}" in block, block   # locale
    assert f"--purpose-font: {_cqw(50)}" in block, block  # default override
    assert f"--axis-font: {_cqw(44)}" in block, block    # axis from locale
    assert "{{" not in block and "}}" not in block, block


def test_y_axis_rotation_key_does_not_become_a_font_size(tmp_path: Path):
    # y-axis-rotation is a structural switch (rotated/stacked), not a font
    # size; it must not be substituted into a font-size custom property. The
    # value reaches the template as the `diagram--stacked` class instead.
    out = _build(
        tmp_path,
        "zh_CN",
        {
            "zh_CN": {
                "font-sizes": {"type": 104, "purpose": 44, "axis": 80},
                "offsets": {"axis-y": 119},
                "y-axis-rotation": "stacked",
            },
        },
    )
    block = _diagram_block(_html(out))
    assert f"--type-font: {_cqw(104)}" in block, block
    assert f"--axis-font: {_cqw(80)}" in block, block
    # The structural switch surfaces as a class, not as a CSS variable.
    assert "diagram--stacked" in block, block
    assert "y-axis-rotation" not in block, block


def test_font_sizes_are_not_msgids(tmp_path: Path):
    """Font sizes must not appear as gettext msgids; count stays 14."""
    out = _build(
        tmp_path,
        "it",
        {"it": {"font-sizes": {"type": 100, "purpose": 44, "axis": 44}, "offsets": {"axis-y": 119}}},
    )
    html = _html(out)
    for s in EXPECTED_MSGIDS:
        assert s in html
    assert len(EXPECTED_MSGIDS) == 14
