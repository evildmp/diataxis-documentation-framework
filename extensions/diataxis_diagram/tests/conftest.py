"""Pytest fixtures for the diataxis_diagram extension tests.

Builds a tiny Sphinx project in a temp directory that exercises the
``.. diataxis-diagram::`` directive with all 12 label fields plus
``:title:`` and ``:desc:``, and provides a gettext build for asserting the
14 translatable strings are extracted into the ``.pot``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from extensions.diataxis_diagram import LABEL_NAMES


# All 14 translatable strings: the 12 label values + :title: and :desc:.
TITLE_TEXT = "A map of documentation types"
DESC_TEXT = "The map is defined by two axes."
LABEL_VALUES = {
    "name-top-left": "Tutorials",
    "name-top-right": "How-to guides",
    "name-bottom-right": "Reference",
    "name-bottom-left": "Explanation",
    "purpose-top-left": "Learning-oriented",
    "purpose-top-right": "Problem-oriented",
    "purpose-bottom-right": "Information-oriented",
    "purpose-bottom-left": "Understanding-oriented",
    "axis-label-left": "Development of skill",
    "axis-label-right": "Application of skill",
    "axis-label-top": "Conceptual grasp",
    "axis-label-bottom": "Practical capacity",
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


# ---------------------------------------------------------------------
# HTML build helpers (Phase 1: pin HTML/CSS behaviour)
#
# The diagram now renders as a scoped ``<div class="diataxis-diagram">`` with
# an inline ``<style>`` (no SVG). The helpers below let the HTML-era tests
# build a Sphinx project from an arbitrary ``index.rst`` and an optional
# ``diataxis_diagram`` typography config, so they can exercise subset
# variants, guides on/off, alt labels, multiple diagrams per page, etc.


def _conf_py(language: str = "en", *, typography: dict | None = None) -> str:
    """A minimal ``conf.py`` enabling the extension with an optional
    ``diataxis_diagram`` config.

    When ``typography`` is None a bare ``en`` entry with the built-in default
    sizes/offsets is supplied, so the build resolves typography without the
    site's real ``conf.py``. When ``typography`` is given it is rendered
    verbatim as the ``diataxis_diagram`` value (callers pass a dict literal
    already shaped like the real config).
    """
    if typography is None:
        typography = {
            "en": {
                "font-sizes": {"type": 104, "purpose": 44, "axis": 44},
                "offsets": {"axis-y": 119},
            }
        }
    return (
        "extensions = [\"extensions.diataxis_diagram\"]\n"
        "project = \"Diátaxis\"\n"
        "author = \"Daniele Procida\"\n"
        f"language = {language!r}\n"
        "master_doc = \"index\"\n"
        "exclude_patterns = []\n"
        f"diataxis_diagram = {typography!r}\n"
    )


def _build_html(
    tmp_path: Path,
    rst: str,
    *,
    language: str = "en",
    typography: dict | None = None,
) -> Path:
    """Build a one-page Sphinx project from a caller-supplied ``index.rst``.

    Returns the ``outdir``; the rendered HTML is at ``outdir / "index.html"``.
    ``typography`` overrides the default minimal ``en`` typography entry; pass
    a dict shaped like the real ``diataxis_diagram`` config (with a ``default``
    key and/or per-locale entries, including ``guides`` if needed).
    """
    _ensure_extensions_importable()
    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"

    src.mkdir()
    (src / "conf.py").write_text(
        _conf_py(language, typography=typography), encoding="utf-8"
    )
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
    return out


def _diagram_blocks(html: str) -> list[str]:
    """Return each rendered diagram's HTML in document order.

    A diagram is emitted as ``<div class=\"diataxis-diagram ...\">...<div ...>...
    </div></div>`` — two nested divs. The regex captures the outer div through
    its closing tag. Tests assert on one or more of these blocks.
    """
    return re.findall(
        r'<div class="diataxis-diagram[^"]*">.*?</div>\s*</div>\s*',
        html,
        re.DOTALL,
    )


_SHARED_CSS_PATH = (Path(__file__).resolve().parent.parent / "static"
                    / "diataxis-diagram.css")


def shared_css() -> str:
    """The extension's shared stylesheet (all diagram CSS lives there now)."""
    return _SHARED_CSS_PATH.read_text(encoding="utf-8")


@pytest.fixture
def built_html(tmp_path: Path) -> Path:
    """Build the default 12-label full diagram in HTML; return ``outdir``."""
    rst = (
        "Welcome\n"
        "=======\n"
        "\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        + "\n".join(
            f'   :{name}: "{value}"' for name, value in LABEL_VALUES.items()
        )
        + "\n"
    )
    return _build_html(tmp_path, rst)
