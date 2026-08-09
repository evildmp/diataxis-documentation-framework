"""Pytest fixtures for the diataxis_diagram extension tests.

Builds a tiny Sphinx project in a temp directory that exercises the
``.. diataxis-diagram::`` directive with all 12 label fields plus ``:alt:``,
and provides a gettext build for asserting the 13 translatable strings
are extracted into the ``.pot``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from extensions.diataxis_diagram import LABEL_NAMES


# All 13 translatable strings: the 12 label values + the :alt: value.
ALT_TEXT = "Diátaxis"
LABEL_VALUES = {
    "tutorials": "Tutorials",
    "how-to": "How-to guides",
    "reference": "Reference",
    "explanation": "Explanation",
    "learning": "Learning-oriented",
    "problem": "Problem-oriented",
    "information": "Information-oriented",
    "understanding": "Understanding-oriented",
    "acquisition": "Serves acquisition of skill",
    "application": "Serves application of skill",
    "action": "Informs action",
    "cognition": "Informs cognition",
}
EXPECTED_MSGIDS = [ALT_TEXT, *LABEL_VALUES.values()]


CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Daniele Procida"
language = {language!r}
master_doc = "index"
exclude_patterns = []
"""


def _svg_content() -> str:
    """A minimal SVG with one <text id="..."> per label name."""
    text_elements = "\n    ".join(
        f'<text id="{name}">placeholder</text>' for name in LABEL_NAMES
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="500" height="120" viewBox="0 0 500 120">\n'
        f"    {text_elements}\n"
        "</svg>\n"
    )


def _index_rst() -> str:
    """An ``index.rst`` invoking ``.. diataxis-diagram::`` with all 12 labels + alt."""
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


def _project_root() -> Path:
    """Path to the repository root (makes the in-tree extensions importable)."""
    return Path(__file__).resolve().parents[2]


def _ensure_extensions_importable() -> None:
    root = _project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _build(
    tmp_path: Path,
    language: str,
    *,
    buildername: str = "html",
) -> tuple[Sphinx, Path]:
    """Build a Sphinx project exercising the diataxis-diagram directive."""
    _ensure_extensions_importable()

    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"
    images = src / "images"

    src.mkdir()
    images.mkdir()
    (src / "conf.py").write_text(
        CONF_PY.format(language=language), encoding="utf-8"
    )
    (src / "index.rst").write_text(_index_rst(), encoding="utf-8")
    (images / "diataxis-diagram-template.svg").write_text(_svg_content(), encoding="utf-8")

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(doctree),
        buildername=buildername,
        freshenv=True,
    )
    app.build()
    return app, out


@pytest.fixture
def built_gettext(tmp_path: Path) -> tuple[Sphinx, Path]:
    """Run the gettext builder; return (app, outdir) containing the .pot files."""
    return _build(tmp_path, "en", buildername="gettext")