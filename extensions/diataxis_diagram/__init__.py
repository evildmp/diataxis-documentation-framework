"""
Content substitutions are taken from the directive's content block, as
``:name: value`` lines. Each ``name`` maps to a ``<text id="name">`` element
in the SVG whose text content is supplied by ``value``, turning the SVG into a
reusable template. Surrounding quotes on the value are stripped, and a comma inside surrounding
quotes is preserved as part of one item rather than splitting (see
``_split_csv``). Substitution
is done by Jinja2 at render time: label ids are hyphenated in the RST and SVG
``id`` attributes, but become underscored top-level variables in the template
context (Jinja2 identifiers cannot contain hyphens), so the SVG uses
``{{ purpose_top_left }}`` etc. inside each ``<text>`` element.

The ``:title:`` and ``:desc:`` options and each label value are
stored on the node as translatable ``nodes.inline`` children (with
``rawsource`` set to the original string), so that ``make gettext`` extracts
them and translated strings are substituted back in at build time. The
``:title:`` and ``:desc:`` values populate the SVG's ``<title id=...>`` and
``<desc id=...>`` elements; together they provide an accessible name and
description for the diagram, exposed via ``aria-labelledby`` on the
``<svg>`` element. Each diagram instance mints a unique ``svg_id`` (and
derived ``title``/``desc``/filter ids) so that when several diagrams appear
on one page their inline ``<style>`` blocks and ``url(#...)`` filter refs don't
collide — the ``<style>`` inside an ``<svg>`` applies document-wide, so every
selector is scoped to ``#{{ svg_id }}``. ``:title:`` and ``:desc:`` are required
options; omitting either raises an error.
"""

from __future__ import annotations

import re
from pathlib import Path

import jinja2
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.transforms import Transform

from sphinx.errors import ExtensionError


# Monotonic counter minting a unique id per ``.. diataxis-diagram::`` instance.
# Each inline SVG's ``<style>`` block applies document-wide (an ``<svg>``'s
# ``<style>`` is not scoped to the SVG), so without per-instance ids the last
# diagram's rules would clobber every earlier one's, and fixed filter ids
# would collide. Sphinx writes each HTML page from a single doctree built
# in a single process, so within-page uniqueness holds even though the counter
# persists across builds (and tests) in the same process; tests therefore assert
# structure, not specific id values.
_svg_id_counter = 0


def _next_svg_id() -> str:
    global _svg_id_counter
    _svg_id_counter += 1
    return f"diataxis-diagram-{_svg_id_counter}"


# Label names that map to <text id="..."> elements in the SVG. Each label
# may take a ``<name>-alt`` counterpart that the SVG renders hidden and
# reveals on hover/focus of the whole ``<svg>`` (see the ``.label-alt`` /
# ``.label-swappable`` CSS in the template).
LABEL_NAMES = (
    "top-left", "top-left-alt",
    "top-right-name", "top-right-name-alt",
    "bottom-right-name", "bottom-right-name-alt",
    "bottom-left-name", "bottom-left-name-alt",
    "purpose-top-left", "purpose-top-left-alt",
    "purpose-top-right", "purpose-top-right-alt",
    "purpose-bottom-right", "purpose-bottom-right-alt",
    "purpose-bottom-left", "purpose-bottom-left-alt",
    "axis-label-left", "axis-label-left-alt",
    "axis-label-right", "axis-label-right-alt",
    "axis-label-top", "axis-label-top-alt",
    "axis-label-bottom", "axis-label-bottom-alt",
    "top-half", "top-half-alt",
    "bottom-half", "bottom-half-alt",
    "left-half", "left-half-alt",
    "right-half", "right-half-alt",
    "need-top-left", "need-top-left-alt",
    "need-top-right-name", "need-top-right-name-alt",
    "need-bottom-right-name", "need-bottom-right-name-alt",
    "need-bottom-left-name", "need-bottom-left-name-alt",
)
# Labels that carry a comma-separated list of strings rather than a single
# value. Each list item is stored as its own translatable inline node with a
# ``<name>-<index>`` field key, so each line is extracted and translated
# independently, then re-collected into an ordered list at render time.
MULTILINE_LABELS = (
    "top-half", "bottom-half", "left-half", "right-half",
    "top-half-alt", "bottom-half-alt", "left-half-alt", "right-half-alt",
)
# Accepted positional args beyond quadrants. ``axes`` still gates
# axis-line visibility (both axes, for backward compatibility); ``x-axis``
# and ``y-axis`` gate them independently. ``axis-labels`` / ``type`` /
# ``purpose`` are kept for backward compatibility but no longer gate
# rendering — label presence in the content block drives that (see
# on_html_visit_diataxis_diagram).
CATEGORY_ARGS = ("axes", "x-axis", "y-axis", "axis-labels", "type", "purpose")
# Valid quadrant names for the optional directive argument. 0 args => all
# four (full diagram). One arg => that quadrant only. Multiple args => the
# union (e.g. "top-left top-right" => top half). The hyphenated form is the
# user-facing RST token and the literal tested against in the template.
QUADRANTS = ("top-left", "top-right", "bottom-left", "bottom-right")
# Each quadrant's position: (horizontal side, vertical side). Used to compute
# the visible region when rendering a subset of the diagram.
_QUADRANT_SIDES = {
    "top-left":     ("left",   "top"),
    "top-right":    ("right",  "top"),
    "bottom-left":  ("left",   "bottom"),
    "bottom-right": ("right",  "bottom"),
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
        "annotation": 100,
        "need": 50,
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
    """Strip one layer of surrounding quotes from a value.

    Whitespace outside the surrounding quotes (e.g. a space between a
    separating comma and the opening quote) is also trimmed; whitespace inside
    the quotes is preserved.
    """
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value


def _split_csv(value: str) -> list[str]:
    """Split on commas that are not inside surrounding quotes.

    A quote character (single or double) opens a quoted span that runs until
    the next matching quote of the same kind; commas inside the span are
    preserved and do not split. The quotes themselves are kept in the output
    and stripped per part by ``_strip_quotes``. Unquoted commas split as
    before, so ``a, b, c`` yields ``['a', ' b', ' c']`` (whitespace trimmed by
    ``_strip_quotes``), while ``"Hello, world", "L2"`` yields
    ``['"Hello, world"', ' "L2"']`` → ``['Hello, world', 'L2']``.
    """
    parts: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    for ch in value:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            buf.append(ch)
            continue
        if ch == ",":
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(ch)
    parts.append("".join(buf))
    return parts


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
    optional_arguments = 10
    option_spec = {
        "title": directives.unchanged,
        "desc": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self):
        node = diataxis_diagram()
        node["classes"] = self.options.get("class", [])
        source = self.state_machine.get_source(self.lineno)

        # Optional positional args: accepted non-quadrant tokens (see
        # CATEGORY_ARGS) and quadrant selectors. Quadrants gate the visible
        # region; label presence in the content block drives which label
        # groups render. ``categories`` is retained only for axis-line
        # visibility (show_x_axis / show_y_axis).
        all_args = set(self.arguments)
        categories = all_args.intersection(CATEGORY_ARGS)
        node["categories"] = categories if categories else None

        quadrants = all_args.difference(CATEGORY_ARGS)
        if not quadrants:
            quadrants = set(QUADRANTS)
        unknown = quadrants.difference(QUADRANTS)
        if unknown:
            raise ExtensionError(
                f"diataxis-diagram: unknown argument "
                f"{', '.join(sorted(unknown))!r}; "
                f"known quadrants: {', '.join(QUADRANTS)}, "
                f"known categories: {', '.join(CATEGORY_ARGS)}"
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
            if name in MULTILINE_LABELS:
                parts = [_strip_quotes(p) for p in _split_csv(value)]
                parts = [p for p in parts if p]
                for j, part in enumerate(parts):
                    node += _make_label_node(f"{name}-{j}", part, source, self.lineno + i)
            else:
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

    # Per-instance ids scope this SVG's <style> and aria/filter refs away from
    # any other diagram on the same page.
    svg_id = _next_svg_id()
    title_id = f"{svg_id}-title"
    desc_id = f"{svg_id}-desc"
    bg_filter_id = f"{svg_id}-label-bg"

    classes = " ".join(node.get("classes", []))
    quadrants = set(node.get("quadrants", set(QUADRANTS)))
    # ``categories`` is retained only for axis-line visibility
    # (show_x_axis / show_y_axis). All other label-group visibility is
    # driven by label presence in the content block combined with quadrant
    # selection.
    categories = node.get("categories")
    # Frame/view bounds use a ``v_`` prefix so the bare ``top``/``bottom``
    # names remain free for the multiline annotation label lists below.
    v_left, v_right, v_top, v_bottom = _quadrant_bounds(
        quadrants, font_sizes["axis"]
    )

    # Multiline annotation labels (``:top-half:`` / ``:bottom-half:`` /
    # ``:left-half:`` / ``:right-half:``) are stored as ``top_half-0`` /
    # ``top_half-1`` / ... field keys, one per line, so each line is translated
    # independently. Re-collect them into ordered lists here, and pop them out
    # of ``labels`` so the generic hyphen→underscore context update below does
    # not emit unused ``top_half_0`` / ``top_half_1`` / ... vars.
    def _collect_lines(prefix):
        indexed = []
        for key in list(labels):
            if key.startswith(f"{prefix}-"):
                try:
                    idx = int(key[len(prefix) + 1 :])
                except ValueError:
                    continue
                indexed.append((idx, labels.pop(key)))
        indexed.sort(key=lambda pair: pair[0])
        return [text for _, text in indexed]

    top = _collect_lines("top-half")
    bottom = _collect_lines("bottom-half")
    left = _collect_lines("left-half")
    right = _collect_lines("right-half")
    top_alt = _collect_lines("top-half-alt")
    bottom_alt = _collect_lines("bottom-half-alt")
    left_alt = _collect_lines("left-half-alt")
    right_alt = _collect_lines("right-half-alt")

    # Scale the annotation font size down as the tallest block grows, so a
    # 4-line block doesn't visually dominate. Aesthetic tuning, not a fit
    # constraint; 0.10 and the 1.5 exponent are the two knobs.  Alt blocks
    # are counted too — they occupy the same position as their defaults.
    n = max(1, len(top), len(bottom), len(left), len(right),
            len(top_alt), len(bottom_alt), len(left_alt), len(right_alt))
    annotation_font_size = font_sizes["annotation"] / (1 + 0.10 * (n - 1) ** 1.5)

    # Annotation anchor points. ``top-half`` / ``bottom-half`` are horizontally
    # centered across the visible region and vertically centered in their half
    # (one quarter / three quarters down from the top edge). ``left-half`` /
    # ``right-half`` are vertically centered across the visible region and
    # horizontally centered in their half (one quarter / three quarters across
    # from the left edge).
    annotation_center_x = (v_left + v_right) / 2
    annotation_center_y = (v_top + v_bottom) / 2
    annotation_top_y = v_top + (v_bottom - v_top) / 4
    annotation_bottom_y = v_top + 3 * (v_bottom - v_top) / 4
    annotation_left_x = v_left + (v_right - v_left) / 4
    annotation_right_x = v_left + 3 * (v_right - v_left) / 4

    show_advert = (
        any(name.endswith("-alt") for name in labels)
        or bool(top_alt or bottom_alt or left_alt or right_alt)
    )

    context = {
        "svg_id": svg_id,
        "title_id": title_id,
        "desc_id": desc_id,
        "bg_filter_id": bg_filter_id,
        "type_font_size": font_sizes["type"],
        "purpose_font_size": font_sizes["purpose"],
        "axis_font_size": font_sizes["axis"],
        "need_font_size": font_sizes["need"],
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
        "show_advert": show_advert,
        # Quadrant selection (set of hyphenated names; all four ⇒ full
        # diagram). Drives the per-label {% if 'q' in quadrants %} gates.
        "quadrants": quadrants,
        # Per-element visibility flags: quadrant membership AND label presence
        # in the content block (default OR alt). show_x_axis / show_y_axis are the
        # sole remnants of the old category mechanism (axes-line visibility);
        # they are not quadrant-gated. ``axes`` (or no category args) enables both
        # for backward compatibility; ``x-axis`` / ``y-axis`` enable each
        # independently.
        "show_x_axis": categories is None or "axes" in categories or "x-axis" in categories,
        "show_y_axis": categories is None or "axes" in categories or "y-axis" in categories,
        "show_axis_label_bottom": ("top-left" in quadrants or "top-right" in quadrants) and ("axis-label-bottom" in labels or "axis-label-bottom-alt" in labels),
        "show_axis_label_top": ("bottom-left" in quadrants or "bottom-right" in quadrants) and ("axis-label-top" in labels or "axis-label-top-alt" in labels),
        "show_axis_label_left": ("top-left" in quadrants or "bottom-left" in quadrants) and ("axis-label-left" in labels or "axis-label-left-alt" in labels),
        "show_axis_label_right": ("top-right" in quadrants or "bottom-right" in quadrants) and ("axis-label-right" in labels or "axis-label-right-alt" in labels),
        "show_top_left": "top-left" in quadrants and ("top-left" in labels or "top-left-alt" in labels),
        "show_top_right_name": "top-right" in quadrants and ("top-right-name" in labels or "top-right-name-alt" in labels),
        "show_bottom_right_name": "bottom-right" in quadrants and ("bottom-right-name" in labels or "bottom-right-name-alt" in labels),
        "show_bottom_left_name": "bottom-left" in quadrants and ("bottom-left-name" in labels or "bottom-left-name-alt" in labels),
        "show_purpose_top_left": "top-left" in quadrants and ("purpose-top-left" in labels or "purpose-top-left-alt" in labels),
        "show_purpose_top_right": "top-right" in quadrants and ("purpose-top-right" in labels or "purpose-top-right-alt" in labels),
        "show_purpose_bottom_right": "bottom-right" in quadrants and ("purpose-bottom-right" in labels or "purpose-bottom-right-alt" in labels),
        "show_purpose_bottom_left": "bottom-left" in quadrants and ("purpose-bottom-left" in labels or "purpose-bottom-left-alt" in labels),
        "show_need_top_left": "top-left" in quadrants and ("need-top-left" in labels or "need-top-left-alt" in labels),
        "show_need_top_right_name": "top-right" in quadrants and ("need-top-right-name" in labels or "need-top-right-name-alt" in labels),
        "show_need_bottom_right_name": "bottom-right" in quadrants and ("need-bottom-right-name" in labels or "need-bottom-right-name-alt" in labels),
        "show_need_bottom_left_name": "bottom-left" in quadrants and ("need-bottom-left-name" in labels or "need-bottom-left-name-alt" in labels),
        # Canvas geometry. The visible region is the bounding box of the
        # selected quadrants (all four ⇒ full diagram). The axes extend to
        # this edge, so frame_* equal the view edges; the viewBox is the
        # (left, top, width, height) derived from them.
        "view_x": v_left,
        "view_y": v_top,
        "view_w": v_right - v_left,
        "view_h": v_bottom - v_top,
        "frame_left": v_left,
        "frame_right": v_right,
        "frame_top": v_top,
        "frame_bottom": v_bottom,
        # Multiline annotation labels (may be empty lists; the template gates
        # each block on truthiness). Always set so StrictUndefined is happy.
        "annotation_font_size": annotation_font_size,
        "annotation_center_x": annotation_center_x,
        "annotation_center_y": annotation_center_y,
        "annotation_top_y": annotation_top_y,
        "annotation_bottom_y": annotation_bottom_y,
        "annotation_left_x": annotation_left_x,
        "annotation_right_x": annotation_right_x,
        "top_half": top,
        "bottom_half": bottom,
        "left_half": left,
        "right_half": right,
        "top_half_alt": top_alt,
        "bottom_half_alt": bottom_alt,
        "left_half_alt": left_alt,
        "right_half_alt": right_alt,
    }
    # Default all scalar label values to "" so the template's {% if <label> %}
    # gates work under StrictUndefined even when only an -alt variant is
    # present. Overridden by the update below where the directive supplied
    # actual values.
    context.update({
        name.replace("-", "_"): ""
        for name in LABEL_NAMES
        if name not in MULTILINE_LABELS
    })
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
