"""Sphinx extension: ``.. diataxis-diagram::`` directive.

Inlines an SVG file directly into the HTML output as raw HTML, instead of
referencing it via ``<img>``.

If this directive is ever dropped in favour of ``<img>`` again, two things
need to be rechecked: (1) CSS features such as ``font-variation-settings``
for variable fonts, which some browsers ignore in a sandboxed ``<img>``
context; and (2) SVG filters, which Safari rasterizes at low resolution in
``<img>`` embeds, blurring text. The Diátaxis diagram relies on both — a
``font-variation-settings`` call on the Skia font and a ``feFlood``/
``feMerge`` filter painting a white background behind the axis labels.

The directive accepts the same ``:class:`` option as ``.. image::`` so existing
layout CSS (e.g. ``img.wider``) can be reused; the class is applied to a
wrapping ``<div>``.

Label substitutions are taken from the directive's content block, as
``:name: value`` lines. Each ``name`` maps to a ``<text id="name">`` element
in the SVG whose text content is replaced by ``value``, turning the SVG into a
reusable template. Surrounding quotes on the value are stripped.

The ``:alt:`` option and each label value are stored on the node as
translatable ``nodes.inline`` children (with ``rawsource`` set to the original
string), so that ``make gettext`` extracts them and translated strings are
substituted back in at build time.
"""

from __future__ import annotations

import re
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.transforms import Transform

from sphinx.errors import ExtensionError


# Label names that map to <text id="..."> elements in the SVG.
LABEL_NAMES = (
    "tutorials",
    "how-to",
    "reference",
    "explanation",
    "learning",
    "problem",
    "information",
    "understanding",
    "acquisition",
    "application",
    "action",
    "cognition",
)
_LABEL_RE = re.compile(r"^:([a-z-]+):\s*(.*)$")


def _strip_quotes(value: str) -> str:
    """Strip one layer of surrounding quotes from a value."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value


class diataxis_diagram(nodes.General, nodes.Element):
    """Placeholder node resolved by the HTML translator visit/depart."""


def _make_label_node(name: str, value: str, source: str, line: int) -> nodes.inline:
    """Build a translatable inline node carrying one label's text.

    ``rawsource`` is the original (untranslated) string, which is what Sphinx's
    gettext extraction reads. ``translatable`` is required because plain
    ``nodes.Inline`` is skipped by default. ``source``/``line`` are required
    because nodes without a source are treated as built-in and skipped.
    """
    node = nodes.inline(value, value)
    node["translatable"] = True
    node["field_key"] = name
    node.source = source
    node.line = line
    return node


class DiataxisDiagram(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "alt": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self):
        src = self.arguments[0].strip()
        node = diataxis_diagram()
        node["src"] = src
        node["classes"] = self.options.get("class", [])
        source = self.state_machine.get_source(self.lineno)

        alt = self.options.get("alt", "")
        if alt:
            node += _make_label_node("alt", alt, source, self.lineno)

        for i, line in enumerate(self.content):
            m = _LABEL_RE.match(line)
            if not m:
                continue
            name, value = m.group(1), m.group(2)
            if name not in LABEL_NAMES:
                raise ExtensionError(
                    f"diataxis-diagram: unknown label option :{name}: "
                    f"(known: {', '.join(LABEL_NAMES)})"
                )
            node += _make_label_node(name, _strip_quotes(value), source, self.lineno + i)

        return [node]


def _resolve_src(src: str, env) -> Path | None:
    """Resolve an ``/images/foo.svg``-style path against the source dir."""
    if src.startswith("/"):
        rel = src.lstrip("/")
    else:
        rel = src
    candidates = [
        Path(env.srcdir) / rel,
        Path(env.srcdir).parent / rel,
        Path(env.srcdir) / "images" / rel,
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


class _CaptureDiataxisDiagramLabels(Transform):
    """Copy translated label text from inline children onto the node.

    Runs after ``Locale`` (priority 20) has rewritten each inline child's
    text with the translated string, and before ``RemoveTranslatableInline``
    (priority 999) strips the inline wrappers and splices bare ``Text`` nodes
    into the parent. Without this, by HTML build time the ``field_key``
    association is gone and the visitor cannot tell labels apart.
    """

    default_priority = 500

    def apply(self, **kwargs):
        for node in self.document.findall(diataxis_diagram):
            labels = {}
            for child in node.children:
                if isinstance(child, nodes.inline) and "field_key" in child:
                    labels[child["field_key"]] = child.astext()
            node["labels"] = labels


def on_html_visit_diataxis_diagram(self, node):
    """Emit the SVG markup inline, wrapped in a div carrying the classes."""
    env = self.builder.env
    src = node.get("src", "")
    path = _resolve_src(src, env)
    if path is None:
        raise ExtensionError(f"diataxis-diagram: file not found: {src!r}")

    text = path.read_text(encoding="utf-8")
    # Strip the XML declaration; it is invalid inside an HTML document.
    if text.lstrip().startswith("<?xml"):
        end = text.find("?>")
        if end != -1:
            text = text[end + 2 :].lstrip()

    labels = dict(node.get("labels", {}))
    alt = labels.pop("alt", "")

    # Substitute <text id="...">text</text> content from directive options.
    for label_id, value in labels.items():
        pattern = re.compile(
            r'(<text[^>]*\bid="' + re.escape(label_id) + r'"[^>]*>)[^<]*(</text>)',
            re.DOTALL,
        )
        new_text, count = pattern.subn(
            lambda m, v=value: m.group(1) + v + m.group(2), text
        )
        if count == 0:
            raise ExtensionError(
                f'diataxis-diagram: no <text id="{label_id}"> found in {src!r}'
            )
        text = new_text

    # Per-language diagram typography (font sizes + y-axis mode) comes from
    # the ``diataxis_diagram_typography`` config in conf.py, keyed by
    # ``config.language``. Font sizes are routed to the inlined SVG's <text>
    # nodes via CSS custom properties emitted on the wrapping <div> below;
    # the matching ``var(--diagram-X-size)`` calls live in _static/diataxis.css.
    # ``y-axis-labels`` is not a font-size — it selects the vertical axis
    # label mode ("rotate" or "stacked") and is handled separately below.
    typography = env.config.diataxis_diagram_typography or {}
    if env.config.language not in typography:
        raise ExtensionError(
            f"diataxis-diagram: language {env.config.language!r} has no entry in "
            f"diataxis_diagram_typography; add one (see source/conf.py)."
        )
    lang_sizes = dict(typography[env.config.language])
    y_axis_mode = lang_sizes.pop("y-axis-labels", "rotate")
    if y_axis_mode not in ("rotate", "stacked"):
        raise ExtensionError(
            f"diataxis-diagram: diataxis_diagram_typography[{env.config.language!r}] "
            f"has unsupported y-axis-labels value {y_axis_mode!r}; "
            f"expected 'rotate' or 'stacked'."
        )
    # Every active locale must supply all three sizes: the CSS rules use
    # var(--diagram-X-size) with NO fallback, so a missing key would leave
    # the property unresolved and collapse the text to the initial ~16px.
    _SIZE_KEYS = ("quadrant", "orientation", "axis")
    missing = [k for k in _SIZE_KEYS if k not in lang_sizes]
    if missing:
        raise ExtensionError(
            f"diataxis-diagram: diataxis_diagram_typography[{env.config.language!r}] "
            f"is missing required size key(s): {', '.join(missing)}."
        )
    custom_props = "; ".join(
        f"--diagram-{k}-size: {lang_sizes[k]}px" for k in _SIZE_KEYS
    )

    # Vertical axis labels: for CJK languages the ``rotate(-90)`` transform
    # tips each glyph on its side. ``stacked`` replaces it with
    # ``writing-mode="vertical-rl"`` so glyphs stay upright and flow
    # top-to-bottom (the CJK convention).
    #
    # The rotated layout anchors each label near the centre (y = ±119) and
    # expands outward along the axis. ``vertical-rl`` flows downward, so to
    # preserve "start near the centre, expand outward" the text-anchor is
    # swapped: the top label (action, y < 0) anchors its bottom at y and grows
    # upward; the bottom label (cognition, y > 0) anchors its top at y and
    # grows downward. Both edits run in one pass via a replacement function,
    # so the result does not depend on attribute order within the <text> tag.
    if y_axis_mode == "stacked":
        def _stack(m: re.Match) -> str:
            tag = m.group(1) + 'writing-mode="vertical-rl"' + m.group(2)
            tag = re.sub(
                r'text-anchor="(start|end)"',
                lambda tm: 'text-anchor="end"' if tm.group(1) == 'start' else 'text-anchor="start"',
                tag,
            )
            return tag

        pattern = re.compile(
            r'(<text\b[^>]*\b)transform="rotate\(-90\s+[0-9.\-]+\s+[0-9.\-]+\)"'
            r'([^>]*>)'
        )
        text, _ = pattern.subn(_stack, text)

    classes = " ".join(node.get("classes", []))
    # role="img" + aria-label exposes the alt text to AT for the inline SVG.
    # ``style`` carries the per-locale font-size custom properties consumed
    # by the .axis/.quadrant/.orientation rules in _static/diataxis.css.
    self.body.append('<div class="diataxis-diagram')
    if classes:
        self.body.append(f" {classes}")
    self.body.append('"')
    if alt:
        self.body.append(f' role="img" aria-label="{self.attval(alt)}"')
    self.body.append(f' style="{custom_props}"')
    self.body.append(">")
    self.body.append(text)
    self.body.append("</div>")
    raise nodes.SkipNode


def on_html_depart_diataxis_diagram(self, node):
    pass


def setup(app):
    app.add_config_value("diataxis_diagram_typography", {}, "env")
    app.add_node(
        diataxis_diagram,
        html=(on_html_visit_diataxis_diagram, on_html_depart_diataxis_diagram),
    )
    app.add_directive("diataxis-diagram", DiataxisDiagram)
    app.add_transform(_CaptureDiataxisDiagramLabels)
    return {"parallel_read_safe": True, "parallel_write_safe": True}