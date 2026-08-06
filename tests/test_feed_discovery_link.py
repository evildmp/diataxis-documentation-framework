"""Test that built pages advertise the Atom feed in <head>.

A <link rel="alternate" type="application/atom+xml"> in the page head is the
standard mechanism by which browsers and feed readers auto-discover a site's
feed. The atomfeed extension injects it via the ``html-page-context`` event.
"""

from __future__ import annotations

import re


_DISCOVERY_RE = re.compile(
    r'<link\s+rel="alternate"\s+type="application/atom\+xml"\s+'
    r'title="(?P<title>[^"]*)"\s+href="(?P<href>[^"]*)"\s*/>'
)


def _head(html: str) -> str:
    start = html.find("<head")
    end = html.find("</head>")
    assert start != -1 and end != -1, "page has no <head>"
    return html[start:end]


def test_feed_discovery_link_in_head(built_outdir):
    html = (built_outdir / "index.html").read_text(encoding="utf-8")
    head = _head(html)

    match = _DISCOVERY_RE.search(head)
    assert match is not None, (
        "no Atom auto-discovery <link> found in <head>; expected "
        '<link rel="alternate" type="application/atom+xml" ...>'
    )

    # Polish build: the feed URL must include the /pl/ language slug.
    href = match.group("href")
    assert href == "https://diataxis.fr/pl/atom.xml", (
        f"discovery link href {href!r} is not the Polish feed URL"
    )

    # Title should be the site's html_title; for the Polish build the
    # translation supplies "Diátaxis  - dokumentacja". Just check it's
    # non-empty and mentions the project name.
    title = match.group("title")
    assert title and "Diátaxis" in title, f"unexpected title {title!r}"
