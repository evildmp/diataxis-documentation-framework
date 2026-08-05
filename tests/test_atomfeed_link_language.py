"""Test that entry <link href> in atom.xml includes the language slug.

When building a translated version of the docs (e.g. Polish), the per-entry
``<link href="..."/>`` in ``atom.xml`` currently points at the default-language
page (``https://diataxis.fr/news.html#news-...``) instead of the translated
page (``https://diataxis.fr/pl/news.html#news-...``).

This test pins the expected behaviour and currently fails.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET


ATOM_NS = "http://www.w3.org/2005/Atom"


def _entry_links(atom_xml_path):
    tree = ET.parse(atom_xml_path)
    root = tree.getroot()
    return [
        entry.find(f"{{{ATOM_NS}}}link").get("href")
        for entry in root.findall(f"{{{ATOM_NS}}}entry")
    ]


def test_entry_link_includes_language_slug(built_atom_xml):
    links = _entry_links(built_atom_xml)

    # Every entry link for the Polish build must point under /pl/.
    for href in links:
        assert "/pl/" in href, (
            f"entry link {href!r} is missing the Polish language slug; "
            f"expected a path under https://diataxis.fr/pl/"
        )

    # Spot-check the first entry explicitly.
    assert links[0] == "https://diataxis.fr/pl/news.html#news-new-atom-feed"
