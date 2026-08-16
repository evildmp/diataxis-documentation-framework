"""Pytest fixtures for the diataxis_diagram extension tests.

Builds a tiny Sphinx project in a temp directory that exercises the
``.. diataxis-diagram::`` directive with all 12 label fields plus
``:title:`` and ``:desc:``, and provides a gettext build for asserting the
14 translatable strings are extracted into the ``.pot``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from extensions.diataxis_diagram import LABEL_NAMES


# All 14 translatable strings: the 12 label values + :title: and :desc:.
TITLE_TEXT = "A map of documentation types"
DESC_TEXT = "The map is defined by two axes."
LABEL_VALUES = {
    "tutorials": "Tutorials",
    "how-to": "How-to guides",
    "reference": "Reference",
    "explanation": "Explanation",
    "orientation-tutorial": "Learning-oriented",
    "orientation-how-to": "Problem-oriented",
    "orientation-reference": "Information-oriented",
    "orientation-explanation": "Understanding-oriented",
    "relation-development": "Development of skill",
    "relation-application": "Application of skill",
    "dimension-theory": "Conceptual grasp",
    "dimension-action": "Practical capacity",
}
EXPECTED_MSGIDS = [TITLE_TEXT, DESC_TEXT, *LABEL_VALUES.values()]


CONF_PY = """\
extensions = ["extensions.diataxis_diagram"]
project = "Diátaxis"
author = "Daniele Procida"
language = {language!r}
master_doc = "index"
exclude_patterns = []
diataxis_diagram = {{
    "en": {{"font-sizes": {{"type": 104, "purpose": 44, "axis": 44}}, "offsets": {{"axis-y": 119}}}},
}}
"""


def _index_rst() -> str:
    """An ``index.rst`` invoking ``.. diataxis-diagram::`` with all 12 labels
    plus ``:title:`` and ``:desc:``."""
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

    src.mkdir()
    (src / "conf.py").write_text(
        CONF_PY.format(language=language), encoding="utf-8"
    )
    (src / "index.rst").write_text(_index_rst(), encoding="utf-8")

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