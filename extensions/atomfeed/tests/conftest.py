"""Pytest fixtures for the atomfeed extension tests.

The tests build a tiny Sphinx project in a temp directory and inspect the
generated ``atom.xml``. We use Sphinx's own build API rather than shelling
out to ``sphinx-build`` so the tests stay fast and self-contained.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sphinx.application import Sphinx


CONF_PY = """\
extensions = ["extensions.atomfeed"]
project = "Diátaxis"
author = "Daniele Procida"
language = {language!r}
atom_feed_base_url = "https://diataxis.fr"
atom_feed_source = "news"
atom_feed_author = author
master_doc = "index"
exclude_patterns = []
"""

NEWS_RST = """\
News & Updates
==============

.. news-item:: New atom feed
   :date: 2026-08-06

   Added an atom feed, https://diataxis.fr/atom.xml.

.. news-item:: Polish translation
   :date: 2026-08-04

   Diátaxis is now available in Polish.
"""

INDEX_RST = """\
Welcome
=======

.. toctree::

   news
"""


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
    """Build a Sphinx project for the given language; return (app, outdir)."""
    _ensure_extensions_importable()

    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"

    src.mkdir()
    (src / "conf.py").write_text(
        CONF_PY.format(language=language), encoding="utf-8"
    )
    (src / "index.rst").write_text(INDEX_RST, encoding="utf-8")
    (src / "news.rst").write_text(NEWS_RST, encoding="utf-8")

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
def built_atom_xml(tmp_path: Path) -> Path:
    """Path to the generated ``atom.xml`` for a Polish build."""
    _app, out = _build(tmp_path, "pl")
    atom_path = out / "atom.xml"
    assert atom_path.exists(), "atom.xml was not generated"
    return atom_path


@pytest.fixture
def built_outdir(tmp_path: Path) -> Path:
    """Built Sphinx outdir for a Polish build (for inspecting rendered HTML)."""
    _app, out = _build(tmp_path, "pl")
    return out


@pytest.fixture
def built_gettext(tmp_path: Path) -> tuple[Sphinx, Path]:
    """Run the gettext builder; return (app, outdir) with the .pot files."""
    return _build(tmp_path, "en", buildername="gettext")
