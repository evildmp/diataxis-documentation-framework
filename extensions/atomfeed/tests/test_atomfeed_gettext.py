"""Test that ``make gettext`` (the ``gettext`` builder) does not crash.

The atomfeed extension's ``on_build_finished`` handler unconditionally
calls ``build_feed``, which accesses ``app.builder.docwriter``. The
``MessageCatalogBuilder`` used by the ``gettext`` builder has no
``docwriter`` attribute, so running ``make gettext`` raises:

    'MessageCatalogBuilder' object has no attribute 'docwriter'

This test pins the expected behaviour (gettext build succeeds).
"""

from __future__ import annotations

import sys
from pathlib import Path

from sphinx.application import Sphinx


CONF_PY = """\
extensions = ["extensions.atomfeed"]
project = "Diátaxis"
author = "Daniele Procida"
language = "en"
atom_feed_base_url = "https://diataxis.fr"
atom_feed_source = "news"
atom_feed_author = author
master_doc = "index"
exclude_patterns = []
gettext_compact = False
"""

NEWS_RST = """\
News & Updates
==============

.. news-item:: New atom feed
   :date: 2026-08-06

   Added an atom feed, https://diataxis.fr/atom.xml.
"""

INDEX_RST = """\
Welcome
=======

.. toctree::

   news
"""


def test_gettext_build_does_not_crash(tmp_path: Path):
    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"
    locale = tmp_path / "locale"

    src.mkdir()
    (src / "conf.py").write_text(CONF_PY, encoding="utf-8")
    (src / "index.rst").write_text(INDEX_RST, encoding="utf-8")
    (src / "news.rst").write_text(NEWS_RST, encoding="utf-8")

    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(doctree),
        buildername="gettext",
        freshenv=True,
    )

    # Should not raise. The gettext builder (MessageCatalogBuilder) has no
    # ``docwriter`` attribute; the feed build must be skipped for non-HTML
    # builders.
    app.build()

    # No atom.xml should be written for a gettext build.
    assert not (out / "atom.xml").exists()
