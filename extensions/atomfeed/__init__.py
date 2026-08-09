"""Sphinx extension: collect ``.. news-item::`` directives and emit atom.xml."""

from __future__ import annotations

import datetime
import html
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

from docutils import nodes
from docutils.parsers.rst import Directive, directives

__version__ = "0.1.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Word characters under re.UNICODE keep accented letters (diátaxis -> diátaxis)
# rather than dropping them, which matters for the Polish/French titles.
SLUG_RE = re.compile(r"[^\w]+", re.UNICODE)


def slugify(text: str) -> str:
    """Return a slug suitable for use as an HTML anchor / id.

    Unicode word characters are preserved, so accented titles (e.g. in the
    Polish or French translations) keep their letters instead of being
    mangled to ASCII.
    """
    slug = SLUG_RE.sub("-", text.strip()).strip("-").lower()
    return slug or "entry"


def rfc3339(date: datetime.date) -> str:
    """RFC 4287 requires a date-time; we have dates only, so midnight UTC."""
    return datetime.datetime.combine(date, datetime.time.min).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def human_date(date: datetime.date) -> str:
    """Format a date for display on the page, e.g. "5 August 2026"."""
    return f"{date.day} {date.strftime('%B')} {date.year}"


def tag_uri(base_url: str, language: str | None, date: datetime.date, slug: str) -> str:
    """Build a ``tag:`` URI per RFC 4151.

    ``tag:<authority>,<date>:<specific>``
    authority = host of atom_feed_base_url
    date     = YYYY-MM-DD of the entry
    specific = "<lang>:<slug>" or just "<slug>"
    """
    host = urlparse(base_url).hostname or "example.org"
    date_part = date.strftime("%Y-%m-%d")
    specific = f"{language}:{slug}" if language else slug
    return f"tag:{host},{date_part}:{specific}"


def absolute_url(base_url: str, page: str, anchor: str | None = None) -> str:
    """Join base_url with a site-relative page (and optional #anchor)."""
    href = urljoin(base_url.rstrip("/") + "/", page.lstrip("/"))
    if anchor:
        href = f"{href}#{anchor}"
    return href


# A fixed, opaque identifier for the feed itself. RFC 4151 tag URIs are meant
# to be stable across rebuilds; using today's date would change the feed id
# every day and make feed readers treat the feed as brand-new each time.
_FEED_TAG_DATE = datetime.date(2026, 1, 1)


class _LinkAbsolutizer(HTMLParser):
    """Rewrite href/src in an HTML fragment to be absolute against base_url.

    Using a real parser (rather than a regex over the raw HTML) means we never
    touch attribute-looking text inside <pre>/<code> blocks, and we see every
    relevant attribute regardless of quoting style.
    """

    _ATTRS = ("href", "src")

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self._base = base_url
        self._out: list[str] = []

    def handle_starttag(self, tag, attrs):
        self._emit(tag, attrs, end=False)

    def handle_startendtag(self, tag, attrs):
        self._emit(tag, attrs, end=True)

    def _emit(self, tag, attrs, *, end):
        rewritten = []
        for name, val in attrs:
            if name in self._ATTRS and val is not None and not val.startswith((
                "http://", "https://", "//", "#", "mailto:", "data:",
            )):
                val = urljoin(self._base, val.lstrip("/"))
            if val is None:
                rewritten.append(name)
            else:
                rewritten.append(f'{name}="{html.escape(val, quote=True)}"')
        suffix = " /" if end else ""
        self._out.append(f"<{tag} {' '.join(rewritten)}{suffix}>" if rewritten else f"<{tag}{suffix}>")

    def handle_endtag(self, tag):
        self._out.append(f"</{tag}>")

    def handle_data(self, data):
        self._out.append(data)

    def handle_entityref(self, name):
        self._out.append(f"&{name};")

    def handle_charref(self, name):
        self._out.append(f"&#{name};")

    def handle_comment(self, data):
        self._out.append(f"<!--{data}-->")

    def result(self) -> str:
        return "".join(self._out)


def absolutize_links(html_fragment: str, base_url: str) -> str:
    """Return *html_fragment* with internal href/src made absolute."""
    if not base_url or not html_fragment:
        return html_fragment
    parser = _LinkAbsolutizer(base_url.rstrip("/") + "/")
    parser.feed(html_fragment)
    parser.close()
    return parser.result()


# ---------------------------------------------------------------------------
# Node + Directive
# ---------------------------------------------------------------------------


class news_item(nodes.Element):
    """Placeholder node replaced at doctree-resolved time."""


class NewsItemDirective(Directive):
    required_arguments = 1  # the title
    final_argument_whitespace = True
    has_content = True
    option_spec = {"date": directives.unchanged_required}

    def run(self):
        title = self.arguments[0].strip()
        date_str = self.options["date"].strip()
        try:
            date = datetime.date.fromisoformat(date_str)
        except ValueError as exc:
            raise self.error(
                f"news-item: :date: must be YYYY-MM-DD, got {date_str!r}"
            ) from exc

        slug = slugify(title)

        # Parse the body content (may be empty).
        if self.content:
            container = nodes.container()
            self.state.nested_parse(self.content, self.content_offset, container)
            body_nodes = list(container.children)
        else:
            body_nodes = []

        # Emit a <section class="news-item" id="news-<slug>"> wrapper as raw
        # HTML so the id lives on the section (not the heading) and the
        # heading is always <h2> regardless of nesting depth. Using raw HTML
        # for the wrapper avoids incrementing docutils' section_level counter,
        # which would otherwise corrupt the level of any real heading that
        # follows the directive.
        anchor_id = f"news-{slug}"
        safe_title = html.escape(title)
        open_section = nodes.raw(
            "",
            f'<section id="{anchor_id}" class="news-item">',
            format="html",
        )
        open_aside = nodes.raw(
            "", '<div class="news-item-aside">', format="html"
        )
        heading_html = (
            f'<h2>{safe_title}'
            f'<a class="headerlink" href="#{anchor_id}" '
            f'title="Link to this heading">¶</a></h2>'
        )
        heading = nodes.raw("", heading_html, format="html")
        close_aside = nodes.raw("", "</div>", format="html")
        close_section = nodes.raw("", "</section>", format="html")

        node = news_item()
        node["date"] = date
        node["title"] = title
        node["slug"] = slug
        node["body_nodes"] = body_nodes  # emitted as siblings above for the page;
        # stashed here so the feed can re-render them at build-finished.

        # Date renders as a plain paragraph with a class, after the heading.
        date_p = nodes.paragraph()
        date_p["classes"].append("date")
        date_p += nodes.Text(human_date(date))

        return [
            open_section,
            open_aside,
            heading,
            date_p,
            close_aside,
            *body_nodes,
            close_section,
            node,
        ]


# ---------------------------------------------------------------------------
# Collection + rendering
# ---------------------------------------------------------------------------


def postprocess_fragment(html_fragment: str, builder) -> str:
    """Absolutize internal links for feed use.

    The fragment comes from the docutils HTML translator's ``fragment`` part,
    which is the naked body content with no theme wrapper, so there is no
    <main> (or any other theme chrome) to strip here.
    """
    base_url = builder.config.atom_feed_base_url or ""
    if not base_url:
        return html_fragment
    return absolutize_links(html_fragment, base_url)


def collect_entries(app, doctree, docname):
    """At doctree-resolved, gather every news-item node with its docname.

    We only collect the parsed body nodes here; HTML rendering happens at
    build-finished, where the builder's writer has a fully-configured
    document/settings to drive the translator.
    """
    env = app.builder.env
    if not hasattr(env, "_atomfeed_entries"):
        env._atomfeed_entries = []

    for node in doctree.traverse(news_item):
        env._atomfeed_entries.append(
            {
                "docname": docname,
                "date": node["date"],
                "title": node["title"],
                "slug": node["slug"],
                "body_nodes": node["body_nodes"],
            }
        )


def render_fragment_html(app, body_nodes) -> str:
    """Render a list of doctree nodes to an HTML fragment.

    We build a fresh document seeded with the builder writer's settings so
    the HTML translator has everything it expects (initial_header_level,
    etc.), then walk each body node through a translator constructed via
    ``builder.create_translator``. We read ``translator.fragment`` (the
    "naked body" part populated by ``depart_document``) rather than
    ``html_body`` (which includes <html>/<head>/<body> chrome).
    """
    if not body_nodes:
        return ""

    builder = app.builder
    # Seed a fresh document with the writer's configured settings + reporter
    # so the HTML translator has everything it expects.
    src_doc = getattr(builder.docwriter, "document", None)
    if src_doc is None:
        # Should not happen for StandaloneHTMLBuilder at build-finished, but
        # guard anyway: render nothing rather than crash.
        return ""
    document = nodes.document(src_doc.settings, src_doc.reporter)
    document["source"] = src_doc.get("source", "")
    document["title"] = src_doc.get("title", "")
    # Attach the body nodes as children of the document so that
    # visit_document/depart_document fire and populate the fragment.
    document.extend(body_nodes)
    translator = builder.create_translator(document, builder)
    document.walkabout(translator)
    return postprocess_fragment("".join(translator.fragment), builder)


# ---------------------------------------------------------------------------
# Feed writing
# ---------------------------------------------------------------------------


ATOM_NS = "http://www.w3.org/2005/Atom"
# Register as the default namespace so ElementTree emits unprefixed Atom
# elements (<feed>, <entry>, ...) without an explicit ``xmlns`` attribute hack
# on the root, and so any future namespaced child is handled correctly.
ET.register_namespace("", ATOM_NS)


def _atom(name: str) -> str:
    """Return a Clark-notation tag name in the Atom namespace."""
    return f"{{{ATOM_NS}}}{name}"


def build_feed(app):
    env = app.builder.env
    entries = getattr(env, "_atomfeed_entries", [])

    base_url = app.config.atom_feed_base_url or "https://example.org"
    language = app.config.language or None
    feed_author = app.config.atom_feed_author or app.config.author or "Unknown"
    feed_title = app.config.html_title or app.config.project or "Feed"
    feed_source_doc = app.config.atom_feed_source  # docname, e.g. "news"

    # Non-default languages are served under a /<lang>/ path prefix on this
    # site (e.g. https://diataxis.fr/pl/news.html); English lives at the root.
    lang_prefix = f"{language}/" if language and language != "en" else ""

    # Sort newest first.
    entries.sort(key=lambda e: e["date"], reverse=True)

    feed = ET.Element(_atom("feed"))
    ET.SubElement(feed, _atom("title")).text = feed_title
    ET.SubElement(
        feed, _atom("link"), rel="self", href=absolute_url(base_url, f"{lang_prefix}atom.xml")
    )
    ET.SubElement(
        feed, _atom("link"), rel="alternate", href=absolute_url(base_url, f"{lang_prefix}{feed_source_doc}.html")
    )
    ET.SubElement(feed, _atom("id")).text = tag_uri(
        base_url, language, _FEED_TAG_DATE, "feed"
    )
    if entries:
        updated = rfc3339(entries[0]["date"])
    else:
        updated = rfc3339(datetime.datetime.now(datetime.timezone.utc).date())
    ET.SubElement(feed, _atom("updated")).text = updated

    author_el = ET.SubElement(feed, _atom("author"))
    ET.SubElement(author_el, _atom("name")).text = feed_author

    for entry in entries:
        page = f"{lang_prefix}{entry['docname']}.html"
        anchor = f"news-{entry['slug']}"
        link = absolute_url(base_url, page, anchor)
        eid = tag_uri(base_url, language, entry["date"], entry["slug"])

        entry_el = ET.SubElement(feed, _atom("entry"))
        ET.SubElement(entry_el, _atom("title")).text = entry["title"]
        ET.SubElement(entry_el, _atom("link"), href=link)
        ET.SubElement(entry_el, _atom("id")).text = eid
        ET.SubElement(entry_el, _atom("updated")).text = rfc3339(entry["date"])
        ET.SubElement(entry_el, _atom("published")).text = rfc3339(entry["date"])

        author_e = ET.SubElement(entry_el, _atom("author"))
        ET.SubElement(author_e, _atom("name")).text = feed_author

        body_html = render_fragment_html(app, entry["body_nodes"])
        if body_html:
            content_el = ET.SubElement(
                entry_el, _atom("content"), type="html"
            )
            content_el.text = body_html

    # Pretty-print with declaration.
    tree = ET.ElementTree(feed)
    ET.indent(tree, space="  ")
    xml_bytes = ET.tostring(
        feed, encoding="utf-8", xml_declaration=True, method="xml"
    )
    out_path = app.outdir / "atom.xml"
    out_path.write_bytes(xml_bytes)


def on_html_page_context(app, pagename, templatename, context, doctree):
    """Inject an Atom auto-discovery <link> into the page head.

    Sphinx themes render ``context['metatags']`` inside <head>, so appending
    here is the canonical way to add feed discovery without a custom template.
    """
    base_url = app.config.atom_feed_base_url or ""
    if not base_url:
        return
    language = app.config.language or "en"
    lang_prefix = f"{language}/" if language != "en" else ""
    href = absolute_url(base_url, f"{lang_prefix}atom.xml")
    title = app.config.html_title or app.config.project or "Feed"
    context["metatags"] = context.get("metatags", "") + (
        f'<link rel="alternate" type="application/atom+xml" '
        f'title="{html.escape(title, quote=True)}" '
        f'href="{html.escape(href, quote=True)}"/>'
    )


def on_build_finished(app, exception):
    if exception is not None:
        return
    # The feed is an HTML artifact; only HTML builders expose the
    # ``docwriter`` we render fragments with. Other builders (notably
    # ``MessageCatalogBuilder`` from ``make gettext``) don't, and would
    # raise ``'MessageCatalogBuilder' object has no attribute 'docwriter'``.
    if getattr(app.builder, "format", None) != "html":
        return
    build_feed(app)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------


def setup(app):
    app.add_node(
        news_item,
        html=(lambda self, node: None, lambda self, node: None),
        latex=(lambda self, node: None, lambda self, node: None),
        text=(lambda self, node: None, lambda self, node: None),
    )
    app.add_directive("news-item", NewsItemDirective)

    app.add_config_value("atom_feed_base_url", None, "env")
    app.add_config_value("atom_feed_source", "news", "env")
    app.add_config_value("atom_feed_author", None, "env")

    app.connect("doctree-resolved", collect_entries)
    app.connect("html-page-context", on_html_page_context)
    app.connect("build-finished", on_build_finished)

    return {"version": __version__, "parallel_read_safe": True}
