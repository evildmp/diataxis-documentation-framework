"""Shared pytest fixtures for the atomfeed extension tests.

The tests build a tiny Sphinx project in a temp directory and inspect the
generated ``atom.xml``. We use Sphinx's own build API rather than shelling
out to ``sphinx-build`` so the tests stay fast and self-contained.
"""

from __future__ import annotations

import shutil
import textwrap
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


@pytest.fixture
def built_atom_xml(tmp_path: Path) -> Path:
    """Build a Sphinx project for the given language and return the outdir.

    Yields the path to the generated ``atom.xml``.
    """
    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"

    src.mkdir()
    (src / "conf.py").write_text(
        CONF_PY.format(language="pl"), encoding="utf-8"
    )
    (src / "index.rst").write_text(INDEX_RST, encoding="utf-8")
    (src / "news.rst").write_text(NEWS_RST, encoding="utf-8")

    # Make the in-tree extensions/ importable as "extensions.atomfeed".
    project_root = Path(__file__).resolve().parent.parent
    import sys
    sys.path.insert(0, str(project_root))

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(doctree),
        buildername="html",
        freshenv=True,
    )
    app.build()

    atom_path = out / "atom.xml"
    assert atom_path.exists(), "atom.xml was not generated"
    return atom_path
