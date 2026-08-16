"""
Content substitutions are taken from the directive's content block, as
``:name: value`` lines. Each ``name`` maps to a ``<text id="name">`` element
in the SVG whose text content is supplied by ``value``, turning the SVG into a
reusable template. Surrounding quotes on the value are stripped. Substitution
is done by Jinja2 at render time: label ids are hyphenated in the RST and SVG
``id`` attributes, but become underscored top-level variables in the template
context (Jinja2 identifiers cannot contain hyphens), so the SVG uses
``{{ orientation_tutorial }}`` etc. inside each ``<text>`` element.

The ``:title:`` and ``:desc:`` options and each label value are
stored on the node as translatable ``nodes.inline`` children (with
``rawsource`` set to the original string), so that ``make gettext`` extracts
them and translated strings are substituted back in at build time. The
``:title:`` and ``:desc:`` values populate the SVG's ``<title id=...>`` and
``<desc id=...>`` elements; together they provide an accessible name and
description for the diagram, exposed via ``aria-labelledby="diagram-map-title
diagram-map-description"`` on the ``<svg>`` element. ``:title:`` and
``:desc:`` are required options; omitting either raises an error.
"""

from __future__ import annotations

import re
from pathlib import Path

import jinja2
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
    "orientation-tutorial",
    "orientation-how-to",
    "orientation-reference",
    "orientation-explanation",
    "relation-development",
    "relation-application",
    "dimension-theory",
    "dimension-action",
)
# Valid quadrant names for the optional directive argument. 0 args ⇒ all
# four (full diagram). One arg ⇒ that quadrant only. Multiple args ⇒ the
# union (e.g. "tutorial how-to" ⇒ top half). The hyphenated form is the
# user-facing RST token and the literal tested against in the template.
QUADRANTS = ("tutorial", "how-to", "explanation", "reference")
# Each quadrant's position: (horizontal side, vertical side). Used to compute
# the visible region when rendering a subset of the diagram.
_QUADRANT_SIDES = {
    "tutorial":    ("left",  "top"),
    "how-to":      ("right", "top"),
    "explanation": ("left",  "bottom"),
    "reference":   ("right", "bottom"),
}
# Full-diagram canvas geometry. The axes span these extents. When rendering a
# subset, the visible region runs from the outer edge to a stub past the
# origin (2 × the resolved axis font-size), so the axes extend to the viewport
# edge with no empty padding.
_FULL_LEFT, _FULL_RIGHT = -960, 960
_FULL_TOP, _FULL_BOTTOM = -540, 540
_LABEL_RE = re.compile(r"^:([a-z-]+):\s*(.*)$")

# Built-in defaults for per-locale diagram typography. A ``default`` key in
# ``diataxis_diagram`` (conf.py) overrides these site-wide, and each
# locale entry overrides on top of that. Locales may omit any key; the resolved
# value falls back through the chain. The structure is nested: ``font-sizes``
# holds the per-class sizes (``type`` / ``purpose`` / ``axis`` map to the SVG's
# ``.type`` / ``.purpose`` / ``.axis`` classes and the ``{{ type_font_size }}``
# / ``{{ purpose_font_size }}`` / ``{{ axis_font_size }}`` placeholders), and
# ``offsets`` holds the per-element-group geometric offsets. ``y-axis-rotation``
# (rotated/stacked) and ``guides`` (bool) are top-level siblings.
DEFAULT_TYPOGRAPHY = {
    "font-sizes": {
        "type": 104,
        "purpose": 44,
        "axis": 42,
    },
    "offsets": {
        "axis-x": 154,
        "type-purpose-x": 154,
        "type-x-correction": 0,
        "axis-y": 120,
        "purpose-y": 120,
        "type-y": 240,
    },
    "y-axis-rotation": "rotated",
    "guides": False,
}


def _merge_layer(base: dict, overlay: dict) -> dict:
    """Deep-merge ``overlay`` onto ``base``; nested dicts merge per-key."""
    result = {k: dict(v) if isinstance(v, dict) else v for k, v in base.items()}
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = _merge_layer(result[k], v)
        else:
            result[k] = v
    return result


def _strip_quotes(value: str) -> str:
    """Strip one layer of surrounding quotes from a value."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value


def _quadrant_bounds(quadrants, axis_font_size):
    """Compute (left, right, top, bottom) for the selected quadrants.

    For a single quadrant the region runs from the outer frame edge to a stub
    of ``2 * axis_font_size`` past the origin. For a union, the bounding box of
    the selected quadrants. All four (the default) yields the full-diagram
    bounds. The axes extend to this region's edge (no empty padding), so frame
    edges equal view edges.
    """
    pad = 2 * axis_font_size
    sides = [_QUADRANT_SIDES[q] for q in quadrants]
    left = min(_FULL_LEFT if h == "left" else -pad for h, _ in sides)
    right = max(_FULL_RIGHT if h == "right" else pad for h, _ in sides)
    top = min(_FULL_TOP if v == "top" else -pad for _, v in sides)
    bottom = max(_FULL_BOTTOM if v == "bottom" else pad for _, v in sides)
    return left, right, top, bottom


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
    required_arguments = 0
    optional_arguments = 4
    option_spec = {
        "title": directives.unchanged,
        "desc": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self):
        node = diataxis_diagram()
        node["classes"] = self.options.get("class", [])
        source = self.state_machine.get_source(self.lineno)

        # Optional positional args select which quadrants to render. 0 args
        # ⇒ all four (full diagram). Unknown names raise immediately.
        quadrants = set(self.arguments) if self.arguments else set(QUADRANTS)
        unknown = quadrants.difference(QUADRANTS)
        if unknown:
            raise ExtensionError(
                f"diataxis-diagram: unknown quadrant "
                f"{', '.join(sorted(unknown))!r}; "
                f"known: {', '.join(QUADRANTS)}"
            )
        node["quadrants"] = quadrants

        if "title" not in self.options:
            raise ExtensionError("diataxis-diagram: missing required option :title:")
        if "desc" not in self.options:
            raise ExtensionError("diataxis-diagram: missing required option :desc:")
        node += _make_label_node("title", self.options["title"], source, self.lineno)
        node += _make_label_node("desc", self.options["desc"], source, self.lineno)

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
    """Emit the SVG markup inline, with classes applied to the <svg>."""
    env = self.builder.env
    template_path = Path(__file__).parent / "diataxis-diagram-template.svg"
    if not template_path.is_file():
        raise ExtensionError(
            f"diataxis-diagram: template not found: {template_path!r}"
        )

    text = template_path.read_text(encoding="utf-8")
    # Strip the XML declaration; it is invalid inside an HTML document.
    if text.lstrip().startswith("<?xml"):
        end = text.find("?>")
        if end != -1:
            text = text[end + 2 :].lstrip()

    labels = dict(node.get("labels", {}))
    title = labels.pop("title", "")
    desc = labels.pop("desc", "")

    # Per-locale diagram typography (font sizes, offsets, y-axis mode) is
    # resolved as a three-layer deep merge: built-in DEFAULT_TYPOGRAPHY, then
    # the ``default`` key in conf.py's diataxis_diagram (site-wide override),
    # then the per-locale entry. Each nested sub-dict (``font-sizes``,
    # ``offsets``) merges per-key, so a locale may override a single size or
    # offset without discarding the rest.
    typography = env.config.diataxis_diagram or {}
    if env.config.language not in typography:
        raise ExtensionError(
            f"diataxis-diagram: language {env.config.language!r} has no entry in "
            f"diataxis_diagram; add one (see source/conf.py)."
        )
    resolved = _merge_layer(DEFAULT_TYPOGRAPHY, typography.get("default", {}))
    resolved = _merge_layer(resolved, typography[env.config.language])

    offsets = resolved["offsets"]
    font_sizes = resolved["font-sizes"]

    y_axis_mode = resolved["y-axis-rotation"]
    if y_axis_mode not in ("rotated", "stacked"):
        raise ExtensionError(
            f"diataxis-diagram: diataxis_diagram[{env.config.language!r}] "
            f"has unsupported y-axis-rotation value {y_axis_mode!r}; "
            f"expected 'rotated' or 'stacked'."
        )

    # Render the SVG template with Jinja2. Autoescape is on because the
    # template is XML (SVG); all values injected here are numeric or
    # controlled attribute strings, so escaping is a no-op in practice but
    # guards against any future string-valued variable.
    # The type labels (Tutorials / Explanation / How-to guides / Reference)
    # are inset from the nominal type/purpose edge towards the origin by
    # ``type-x-correction`` so their larger glyphs don't overflow the frame.
    type_x = offsets["type-purpose-x"] - offsets["type-x-correction"]

    classes = " ".join(node.get("classes", []))
    quadrants = set(node.get("quadrants", set(QUADRANTS)))
    left, right, top, bottom = _quadrant_bounds(quadrants, font_sizes["axis"])
    context = {
        "type_font_size": font_sizes["type"],
        "purpose_font_size": font_sizes["purpose"],
        "axis_font_size": font_sizes["axis"],
        "axis_x": offsets["axis-x"],
        "type_purpose_x": offsets["type-purpose-x"],
        "type_x": type_x,
        "axis_y": offsets["axis-y"],
        "purpose_y": offsets["purpose-y"],
        "type_y": offsets["type-y"],
        "y_axis_mode": y_axis_mode,
        "guides": resolved["guides"],
        "title": title,
        "desc": desc,
        "class": classes,
        # Quadrant selection (set of hyphenated names; all four ⇒ full
        # diagram). Drives the per-label {% if 'q' in quadrants %} gates.
        "quadrants": quadrants,
        # Canvas geometry. The visible region is the bounding box of the
        # selected quadrants (all four ⇒ full diagram). The axes extend to
        # this edge, so frame_* equal the view edges; the viewBox is the
        # (left, top, width, height) derived from them.
        "view_x": left,
        "view_y": top,
        "view_w": right - left,
        "view_h": bottom - top,
        "frame_left": left,
        "frame_right": right,
        "frame_top": top,
        "frame_bottom": bottom,
    }
    context.update({k.replace("-", "_"): v for k, v in labels.items()})
    text = (
        jinja2.Environment(autoescape=True, undefined=jinja2.StrictUndefined)
        .from_string(text)
        .render(**context)
    )

    self.body.append(text)
    raise nodes.SkipNode


def on_html_depart_diataxis_diagram(self, node):
    pass


def setup(app):
    app.add_config_value("diataxis_diagram", {}, "env")
    app.add_node(
        diataxis_diagram,
        html=(on_html_visit_diataxis_diagram, on_html_depart_diataxis_diagram),
    )
    app.add_directive("diataxis-diagram", DiataxisDiagram)
    app.add_transform(_CaptureDiataxisDiagramLabels)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
