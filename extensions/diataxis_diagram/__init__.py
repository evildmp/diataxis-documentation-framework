"""
Content substitutions are taken from the directive's content block, as
``:name: value`` lines. Each ``name`` maps to a labelled slot in the HTML
template whose text content is supplied by ``value``. Surrounding quotes on
the value are stripped, and a comma inside surrounding quotes is preserved as
part of one item rather than splitting (see ``_split_csv``). Substitution is
done by Jinja2 at render time: label ids are hyphenated in the RST and in the
template's CSS class names, but become underscored top-level variables in the
template context (Jinja2 identifiers cannot contain hyphens), so the template
uses ``{{ purpose_top_left }}`` etc. inside each slot.

The ``:title:`` and ``:desc:`` options and each label value are stored on the
node as translatable ``nodes.inline`` children (with ``rawsource`` set to the
original string), so that ``make gettext`` extracts them and translated
strings are substituted back in at build time. The ``:title:`` and ``:desc:``
values are concatenated into the ``aria-label`` of the diagram's ``<div>``
(``role="img"``, ``tabindex="0"``), providing an accessible name and
description. Each diagram instance mints a unique ``diagram_id`` so that when
several diagrams appear on one page their inline ``<style>`` blocks don't
collide — the ``<style>`` applies document-wide, so every selector is scoped
to ``#{{ diagram_id }}``. ``:title:`` and ``:desc:`` are required options;
omitting either raises an error.
"""

from __future__ import annotations

import re
import math
import random
from pathlib import Path

import jinja2
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.transforms import Transform

from sphinx.errors import ExtensionError


# Monotonic counter minting a unique id per ``.. diataxis-diagram::`` instance.
# Each diagram's scoped ``<style>`` block (and its ``@keyframes`` name) is
# prefixed with this id so the rules don't collide when several diagrams
# appear on one page — an inline ``<style>`` applies document-wide, so
# without per-instance ids the last diagram's rules would clobber every
# earlier one's. Sphinx writes each HTML page from a single doctree built
# in a single process, so within-page uniqueness holds even though the
# counter persists across builds (and tests) in the same process; tests
# therefore assert structure, not specific id values.
_diagram_id_counter = 0


def _next_diagram_id() -> str:
    global _diagram_id_counter
    _diagram_id_counter += 1
    return f"diataxis-diagram-{_diagram_id_counter}"


# Label names that map to slot elements in the HTML template. Each label
# may take a ``<name>-alt`` counterpart that the template renders hidden and
# reveals on hover/focus of the diagram (see the ``.label-alt`` /
# ``.label-swappable`` CSS in the template), and a ``<name>-both`` counterpart
# that is always visible (no swap classes). The ``-alt``/``-both`` suffixes
# mirror the positional directive args (see ``run``).
LABEL_NAMES = (
    "name-top-left", "name-top-left-alt", "name-top-left-both",
    "name-top-right", "name-top-right-alt", "name-top-right-both",
    "name-bottom-right", "name-bottom-right-alt", "name-bottom-right-both",
    "name-bottom-left", "name-bottom-left-alt", "name-bottom-left-both",
    "purpose-top-left", "purpose-top-left-alt", "purpose-top-left-both",
    "purpose-top-right", "purpose-top-right-alt", "purpose-top-right-both",
    "purpose-bottom-right", "purpose-bottom-right-alt", "purpose-bottom-right-both",
    "purpose-bottom-left", "purpose-bottom-left-alt", "purpose-bottom-left-both",
    "axis-label-left", "axis-label-left-alt", "axis-label-left-both",
    "axis-label-right", "axis-label-right-alt", "axis-label-right-both",
    "axis-label-top", "axis-label-top-alt", "axis-label-top-both",
    "axis-label-bottom", "axis-label-bottom-alt", "axis-label-bottom-both",
    "top-half", "top-half-alt", "top-half-both",
    "bottom-half", "bottom-half-alt", "bottom-half-both",
    "left-half", "left-half-alt", "left-half-both",
    "right-half", "right-half-alt", "right-half-both",
    "need-top-left", "need-top-left-alt", "need-top-left-both",
    "need-top-right-name", "need-top-right-name-alt", "need-top-right-name-both",
    "need-bottom-right-name", "need-bottom-right-name-alt", "need-bottom-right-name-both",
    "need-bottom-left-name", "need-bottom-left-name-alt", "need-bottom-left-name-both",
)
# Labels that carry a comma-separated list of strings rather than a single
# value. Each list item is stored as its own translatable inline node with a
# ``<name>-<index>`` field key, so each line is extracted and translated
# independently, then re-collected into an ordered list at render time.
MULTILINE_LABELS = (
    "top-half", "bottom-half", "left-half", "right-half",
    "top-half-alt", "bottom-half-alt", "left-half-alt", "right-half-alt",
    "top-half-both", "bottom-half-both", "left-half-both", "right-half-both",
)
# Accepted positional args beyond quadrants. ``axes`` still gates
# axis-line visibility (both axes, for backward compatibility); ``x-axis``
# and ``y-axis`` gate them independently. ``axis-labels`` / ``type`` /
# ``purpose`` are kept for backward compatibility but no longer gate
# rendering — label presence in the content block drives that (see
# on_html_visit_diataxis_diagram).
CATEGORY_ARGS = ("axes", "x-axis", "y-axis", "axis-labels", "type", "purpose")
# Flag-style positional args (present/absent, no value) that drive a visual
# effect rather than quadrant or category selection. Like category args they
# are stripped of ``-alt`` / ``-both`` in ``run`` and may carry those suffixes,
# but they gate no axis line and select no quadrant, so they must be pulled
# out of ``quadrants`` before the unknown-arg check (see ``run``).
FLAG_ARGS = ("blur", "collapse")
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
# holds the per-class sizes (``type`` / ``purpose`` / ``axis`` / ``need`` /
# ``annotation`` map to the template's CSS classes of the same name and the
# ``{{ type_font }}`` / ``{{ purpose_font }}`` / ``{{ axis_font }}`` /
# ``{{ need_font }}`` / ``{{ annotation_font }}`` CSS-variable values), and
# ``offsets`` holds the per-element-group geometric offsets. ``y-axis-rotation``
# (rotated/stacked) is a top-level sibling. ``guides`` is a top-level dict
# ``{"show": bool, "x": int, "y": int}`` — ``show`` gates the construction
# guide lines, ``x``/``y`` (source px, same units as ``offsets``) are the
# horizontal/vertical offsets of the inner guide lines from the axes.
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
    "guides": {"show": False, "x": 154, "y": 120},
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


# Canvas geometry used by ``_html_geometry``. The axes span these extents; the
# visible region for a subset runs from the outer edge to a stub of
# ``2 * axis_font_size`` past the origin.
_FULL_HALF_W = 960
_FULL_HALF_H = 540


def _variant_name(quadrants) -> str:
    """Class token for ``diagram--{{ variant }}`` from the selected quadrants."""
    if quadrants == set(QUADRANTS):
        return "full"
    if quadrants == {"top-left", "top-right"}:
        return "top"
    if quadrants == {"bottom-left", "bottom-right"}:
        return "bottom"
    if quadrants == {"top-left", "bottom-left"}:
        return "left"
    if quadrants == {"top-right", "bottom-right"}:
        return "right"
    if len(quadrants) == 1:
        return next(iter(quadrants))
    # Diagonal or other unions have no named variant; fall back to a joined
    # token so the class is still present and unique per selection.
    return "-".join(sorted(quadrants))


def _html_geometry(quadrants, font_sizes, offsets, guides):
    """Compute the HTML grid geometry and CSS variables for the selection.

    The diagram is laid out as a CSS grid whose tracks are the conceptual
    regions of the Diátaxis map: two columns (left/right of the y-axis) and
    two or three rows (top quadrants / central axis band / bottom quadrants).
    Each side is either the full half-extent (960 / 540) or a stub of
    ``2 * axis_font_size`` past the origin. Overlays (the axis lines, the
    axis-cross labels,
    annotations and the advert cue) are absolutely positioned within
    full-span grid cells.

    Returns a dict of strings ready to interpolate into the template's
    inline style and class attribute. Font sizes are expressed in ``cqw``
    (container query width units) so the whole diagram scales with its
    container; the geometric offsets are constant percentages (denominators
    are the fixed 960px quadrant width / the per-variant top-row height).

    ``guides`` is the resolved dict ``{"show": bool, "x": int, "y": int}``.
    ``x``/``y`` are the source-px offsets of the inner guide lines from the
    axes (same units as ``offsets`` entries); they are independent of
    ``type-purpose-x`` / ``purpose-y``.
    """
    axis_font = font_sizes["axis"]
    pad = 2 * axis_font
    central_half = offsets["axis-y"]
    type_y = offsets["type-y"]
    type_purpose_x = offsets["type-purpose-x"]
    axis_x = offsets["axis-x"]
    type_x = type_purpose_x - offsets["type-x-correction"]

    guides_x = guides["x"]
    guides_y = guides["y"]

    has_left = "top-left" in quadrants or "bottom-left" in quadrants
    has_right = "top-right" in quadrants or "bottom-right" in quadrants
    has_top = "top-left" in quadrants or "top-right" in quadrants
    has_bottom = "bottom-left" in quadrants or "bottom-right" in quadrants

    # Column / row track sizes in canvas px (each side is full or stub).
    left_w = _FULL_HALF_W if has_left else pad
    right_w = _FULL_HALF_W if has_right else pad
    quad_h = _FULL_HALF_H - central_half          # a full quadrant row height
    top_row_h = quad_h if has_top else 0
    bottom_row_h = quad_h if has_bottom else 0
    # The central band is [-central_half, +central_half]; a cut side exposes
    # only down to the stub, so the visible central height is:
    central_h = (central_half if has_top else pad) + (central_half if has_bottom else pad)

    width = left_w + right_w
    height = top_row_h + central_h + bottom_row_h

    # Grid columns: ``1fr 1fr`` when both sides are full (visually equal),
    # else explicit percentages (quadrant subsets have a stub column).
    if left_w == right_w:
        grid_cols = "1fr 1fr"
    else:
        grid_cols = f"{left_w / width * 100:.4f}% {right_w / width * 100:.4f}%"

    # Grid rows: always explicit percentages (the central row is never the
    # same height as a quadrant row).
    row_sizes = [s for s in (top_row_h, central_h, bottom_row_h) if s]
    grid_rows = " ".join(f"{s / height * 100:.4f}%" for s in row_sizes)

    # The central row is the LAST row for ``top*`` variants (has_top, not
    # has_bottom) and the FIRST row for ``bottom*`` variants; otherwise the
    # middle row of three.
    if has_top and has_bottom:
        central_row = 2
    elif has_top:
        central_row = 2
    else:
        central_row = 1

    # Axis position as a % of the visible region: distance from the visible
    # edge to the origin (the axes cross at 0). The visible top edge is the
    # real top (540 above the origin) when top quadrants are shown, else the
    # stub (pad); the visible left edge is the real left (960) when left
    # quadrants are shown, else the stub.
    axis_x_pos = (_FULL_HALF_W if has_left else pad) / width * 100
    axis_y_pos = ((quad_h + central_half) if has_top else pad) / height * 100
    axis_high = axis_y_pos > 50
    axis_low = axis_y_pos < 50

    # Guide construction lines (gated by the `guides` bool in the template).
    # Vertical guides at +/-guides_x; horizontal guides at +/-guides_y
    # (source px, same units as `offsets` entries). Positions are % of the
    # visible region from its top-left corner; the frame border is at 0/100%.
    # Off-region guides (e.g. +154 in a single-quadrant view) land outside
    # 0-100% and are clipped by `overflow: hidden`.
    guide_v_left = axis_x_pos - guides_x / width * 100
    guide_v_right = axis_x_pos + guides_x / width * 100
    guide_h_top = axis_y_pos - guides_y / height * 100
    guide_h_bottom = axis_y_pos + guides_y / height * 100

    g = math.gcd(round(width), round(height))
    aspect_ratio = f"{round(width) // g} / {round(height) // g}"

    def cqw(px):
        return f"{px / width * 100:.4f}cqw"

    def pct(v):
        return f"{v:.4f}%"

    return {
        "variant": _variant_name(quadrants),
        "width": width,
        "height": height,
        "grid_cols": grid_cols,
        "grid_rows": grid_rows,
        "aspect_ratio": aspect_ratio,
        "axis_x_pos": pct(axis_x_pos),
        "axis_y_pos": pct(axis_y_pos),
        "central_row": central_row,
        "axis_high": axis_high,
        "axis_low": axis_low,
        # Font sizes scale with the container width.
        "type_font": cqw(font_sizes["type"]),
        "purpose_font": cqw(font_sizes["purpose"]),
        "axis_font": cqw(font_sizes["axis"]),
        "need_font": cqw(font_sizes["need"]),
        # Geometric offsets are constant: the denominator is the fixed 960px
        # quadrant cell width, so these do not change across variants.
        "type_x_pct": pct(type_x / _FULL_HALF_W * 100),
        "purpose_x_pct": pct(type_purpose_x / _FULL_HALF_W * 100),
        # Axis-label x-offset: structural, always exactly `axis-x` (154px).
        # Denominator is the per-variant container width (NOT the fixed 960
        # half) so it is exact across full / left-only / right-only /
        # single-quadrant views. The 2× factor accounts for the template's
        # `/2` in the calc() that consumes this variable.
        "axis_x_label_pct": pct(2 * axis_x / width * 100),
        # Axis-label y-offset: structural, always exactly `axis-y` (110px).
        # Denominator is the per-variant container height (NOT the fixed
        # 540 half) so it is exact across full / top-only / bottom-only /
        # single-quadrant views.
        "axis_y_label_pct": pct(central_half / height * 100),
        # type-y offset is measured from the inner edge of the quadrant row;
        # denominator is the (constant) quadrant row height.
        "type_y_pct": pct((type_y - central_half) / quad_h * 100),
        # Axis stroke gets a 1px floor so it stays visible at small sizes.
        "axis_stroke": f"max({cqw(2)}, 1px)",
        # Guide construction lines (frame + purpose-edge cross), #999, 1px with
        # a 1px floor; rendered only when the `guides` bool is true.
        "guide_v_left": pct(guide_v_left),
        "guide_v_right": pct(guide_v_right),
        "guide_h_top": pct(guide_h_top),
        "guide_h_bottom": pct(guide_h_bottom),
        "guide_stroke": f"max({cqw(1)}, 1px)",
        # Advert-cue sizes (60px circle, 3px ring border, 12px dots, 30px inset).
        "cue_size": cqw(60),
        "cue_border": cqw(3),
        "cue_dot": cqw(12),
        "cue_inset": cqw(30),
        # Purpose label letter-spacing.
        "purpose_ls": cqw(2.2),
    }


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

        # Optional positional args: each may carry an ``-alt`` suffix marking
        # it as the hover-revealed variant, or a ``-both`` suffix marking it as
        # always visible (mirroring the ``-alt`` / ``-both`` label properties;
        # see the ``.label-alt`` / ``.label-swappable`` swap in the template).
        # The suffix is stripped to get the base arg, which drives quadrant
        # selection and axis-line visibility exactly as before; the ``-alt`` /
        # ``-both`` flags are tracked on the node so axis lines can swap on
        # hover (``-alt``) or render plain (``-both``). The suffixes are
        # accepted on any arg, but only ``x-axis`` / ``y-axis`` / ``axes`` gate
        # a swappable element (an axis line), so ``-alt`` / ``-both`` on a
        # quadrant or no-op category arg is a no-op (the base arg still
        # applies). ``-both`` never wires a swap or fires the advert cue.
        default_args: set[str] = set()
        alt_args: set[str] = set()
        both_args: set[str] = set()
        for arg in self.arguments:
            if arg.endswith("-alt"):
                alt_args.add(arg[: -len("-alt")])
            elif arg.endswith("-both"):
                both_args.add(arg[: -len("-both")])
            else:
                default_args.add(arg)
        node["default_args"] = default_args
        node["alt_args"] = alt_args
        node["both_args"] = both_args

        all_args = default_args | alt_args | both_args
        categories = all_args.intersection(CATEGORY_ARGS)
        node["categories"] = categories if categories else None

        quadrants = all_args.difference(CATEGORY_ARGS)
        # Flag args (e.g. ``blur``) are neither quadrants nor categories; pull
        # them out before the unknown-quadrant check so they don't raise. They
        # are tracked via ``default_args`` / ``alt_args`` / ``both_args`` (the
        # suffix strip above already handled ``blur`` / ``blur-alt`` /
        # ``blur-both``); removing them here only prevents the error.
        quadrants = {q for q in quadrants if q not in FLAG_ARGS}
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
    """Emit the HTML/CSS markup inline, with classes applied to the diagram."""
    env = self.builder.env
    template_path = Path(__file__).parent / "diataxis-diagram-template.html"
    if not template_path.is_file():
        raise ExtensionError(
            f"diataxis-diagram: template not found: {template_path!r}"
        )
    text = template_path.read_text(encoding="utf-8")

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

    # `guides` is a dict {"show": bool, "x": int, "y": int}. For backward
    # compatibility, accept a bare bool (old shape) and read x/y from offsets
    # (type-purpose-x / purpose-y) so the old behaviour is reproduced exactly.
    guides_cfg = resolved.get("guides", {})
    if isinstance(guides_cfg, bool):
        guides_cfg = {
            "show": guides_cfg,
            "x": offsets["type-purpose-x"],
            "y": offsets["purpose-y"],
        }
    elif not isinstance(guides_cfg, dict):
        guides_cfg = {"show": False, "x": 154, "y": 120}

    # Per-instance id scopes this diagram's <style> block and @keyframes name
    # away from any other diagram on the same page (an inline <style> applies
    # document-wide, so every selector is prefixed with #{{ diagram_id }}).
    diagram_id = _next_diagram_id()

    user_classes = " ".join(node.get("classes", []))
    quadrants = set(node.get("quadrants", set(QUADRANTS)))
    # Axis-line args may carry an ``-alt`` or ``-both`` suffix (parsed in
    # ``run``): ``x-axis`` / ``y-axis`` / ``axes`` given without a suffix are
    # the default axis lines; the same given with ``-alt`` are the
    # hover-revealed variants; the same given with ``-both`` are always
    # visible (plain, no swap classes).
    # ``categories_default`` / ``categories_alt`` / ``categories_both`` are the
    # base category args split by suffix; ``has_axis_alt`` is the swap trigger
    # for the default axis lines (``-both`` does NOT trigger a swap).
    default_args = set(node.get("default_args", set()))
    alt_args = set(node.get("alt_args", set()))
    both_args = set(node.get("both_args", set()))
    categories_default = default_args.intersection(CATEGORY_ARGS)
    categories_alt = alt_args.intersection(CATEGORY_ARGS)
    categories_both = both_args.intersection(CATEGORY_ARGS)
    _AXIS_LINE_ARGS = ("x-axis", "y-axis", "axes")
    has_axis_alt = bool(categories_alt.intersection(_AXIS_LINE_ARGS))

    geometry = _html_geometry(quadrants, font_sizes, offsets, guides_cfg)

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
        return [t for _, t in indexed]

    top = _collect_lines("top-half")
    bottom = _collect_lines("bottom-half")
    left = _collect_lines("left-half")
    right = _collect_lines("right-half")
    top_alt = _collect_lines("top-half-alt")
    bottom_alt = _collect_lines("bottom-half-alt")
    left_alt = _collect_lines("left-half-alt")
    right_alt = _collect_lines("right-half-alt")
    top_both = _collect_lines("top-half-both")
    bottom_both = _collect_lines("bottom-half-both")
    left_both = _collect_lines("left-half-both")
    right_both = _collect_lines("right-half-both")

    # Scale the annotation font size down as the tallest block grows, so a
    # 4-line block doesn't visually dominate. Aesthetic tuning, not a fit
    # constraint; 0.10 and the 1.5 exponent are the two knobs.  Alt and both
    # blocks are counted too — they occupy the same position as their
    # defaults.
    n = max(1, len(top), len(bottom), len(left), len(right),
            len(top_alt), len(bottom_alt), len(left_alt), len(right_alt),
            len(top_both), len(bottom_both), len(left_both), len(right_both))
    annotation_font_size = font_sizes["annotation"] / (1 + 0.10 * (n - 1) ** 1.5)
    annotation_font = f"{annotation_font_size / geometry['width'] * 100:.4f}cqw"

    # --- Blur effect (``blur`` / ``blur-alt`` / ``blur-both``) -------------
    # A flag-style positional arg (like ``axes``): present or absent, no value.
    # When present, each of the 12 quadrant content slots is transformed with
    # two randomized effects drawn once per slot at build time:
    #   1. Inward pull — moved toward the diagram origin (where the axes
    #      cross) by a random fraction ``f ∈ [0.10, 0.25]`` of the slot's
    #      distance to the origin: ``new_pos = slot_pos + f*(origin - slot_pos)``.
    #   2. Rotation — rotated by a random angle in ``[5°, 10°]`` with a random
    #      sign (CW/CCW).
    # ``blur`` (no suffix) applies unhovered; ``blur-alt`` applies on hover
    # (the default blurred spans become ``label-swappable`` and the alt
    # blurred spans become ``label-alt`` — same random values, one draw);
    # ``blur-both`` applies always (plain, no swap). ``-alt`` fires the advert
    # cue and contributes to ``label_swap_active``; ``-both`` does neither.
    # Only the 12 quadrant content labels (type / purpose / need in each of
    # the four slots) are blurred — axis labels sit on the axes and would be
    # rotated/clipped by their own transforms, so they are excluded.
    blur_default = "blur" in default_args
    blur_alt = "blur" in alt_args
    blur_both = "blur" in both_args
    collapse_default = "collapse" in default_args
    collapse_alt = "collapse" in alt_args
    collapse_both = "collapse" in both_args
    # The 12 quadrant slots keyed by their ``show_*`` flag name + a vector from
    # the slot centre to the origin, expressed as a fraction of the visible
    # width / height so it converts to a ``cqw`` / (height/width-scaled) ``cqw``
    # translate. The slot centre sits at the inner corner of its cell, one
    # ``--type-x-pct`` / ``--type-y-pct`` (type/need) or ``--purpose-x-pct`` /
    # 0 (purpose) inset from the cell edge — but for the blur direction only the
    # sign matters (toward the origin), so the slot centre is approximated as
    # the quadrant centre: a vector of (±0.5, ±0.5) of the half-extent. The pull
    # is applied along this direction by ``f``, so a slot at the top-left
    # quadrant centre pulls toward (0,0) (down-right); the exact magnitude is
    # not visually load-bearing because ``f`` is randomised and the pull is a
    # fraction of the slot→origin distance, not a fixed offset.
    #
    # The vector from slot centre to origin, in the same units as the visible
    # width / height (the denominators that ``cqw`` / the height-scaled ``cqw``
    # are fractions of). For the full diagram the origin is at (50%, 50%) of the
    # visible region, and a slot centre is at (25%, 25%) / (75%, 25%) /
    # (25%, 75%) / (75%, 75%), so the centre→origin vector is (±25%, ±25%) of
    # the half-extent. For subset variants the origin shifts toward the cut
    # edge and the slot centres shift with it; rather than recompute per
    # variant, the pull is applied as a fraction of the *visible-region* vector
    # to the origin, which keeps the direction (toward the origin) correct and
    # the magnitude in the same order across variants. The visible-region
    # origin position is ``axis_x_pos`` / ``axis_y_pos`` (already computed as
    # percentages); the slot centres are at (25/75, 25/75)% of the region. So
    # the centre→origin vector is ``(axis_x_pos - slot_cx, axis_y_pos - slot_cy)``
    # in % of the visible region; converted to ``cqw`` for x and to a
    # height-scaled ``cqw`` for y (cqh is unavailable: the container is
    # inline-size, so only cqw exists; the y component is rescaled by the
    # aspect ratio's height/width to land in the same physical units).
    axis_x_pct = float(geometry["axis_x_pos"].rstrip("%"))
    axis_y_pct = float(geometry["axis_y_pos"].rstrip("%"))
    _height_over_width = geometry["height"] / geometry["width"]
    # Slot centres (% of the visible region): the inner-corner of each cell,
    # at the type/purpose/need anchor offset. The anchor differs per label
    # kind (type/need inset by --type-x-pct/--type-y-pct; purpose by
    # --purpose-x-pct at the central-row edge), but all that matters for the
    # *direction* of the pull is which side of the origin the slot is on, so a
    # single centre per quadrant is used (top-left=25/25, top-right=75/25,
    # bottom-left=25/75, bottom-right=75/75). The randomised ``f`` in [0.20,
    # 0.40] sets the magnitude as a fraction of the centre→origin distance.
    _slot_centres = {
        "top_left":         (0.25, 0.25),
        "top_right":        (0.75, 0.25),
        "bottom_left":      (0.25, 0.75),
        "bottom_right":     (0.75, 0.75),
    }
    # Map each blurred slot's ``show_*`` flag name to its base CSS transform —
    # the existing centring transform the slot's ``> span`` already has (e.g.
    # ``translateY(50%)`` for a type-top-left). The inline ``style`` transform
    # overrides the CSS one, so the base must be repeated inline for the blur
    # to compose rather than replace it (otherwise the slot jumps to its
    # unscaled anchor and the blur lands in the wrong place).
    _slot_base_transform = {
        "top_left":         "translateY(50%)",
        "top_right":        "translateY(50%)",
        "bottom_left":      "translateY(-50%)",
        "bottom_right":     "translateY(-50%)",
    }
    # Each slot's flag name in the context (gates the slot ``<div>``) + its
    # kind prefix (used to look up the slot's flag). Type and need share the
    # same anchors; purpose sits on the central-row edge but uses the same
    # pull direction (toward the origin), so it reuses the same centre map.
    # The blur is applied to every quadrant slot that renders, keyed by the
    # slot's ``show_*`` flag — the template reads ``blur_transforms[<flag>]``
    # and, when present, appends ``style="transform: <base> translate(...) rotate(...)"``
    # to the slot's default / alt / both span.
    _slot_flag_names = (
        ("top_left",               "show_name_top_left"),
        ("top_right",              "show_name_top_right"),
        ("bottom_left",           "show_name_bottom_left"),
        ("bottom_right",          "show_name_bottom_right"),
        ("top_left",              "show_purpose_top_left"),
        ("top_right",             "show_purpose_top_right"),
        ("bottom_left",          "show_purpose_bottom_left"),
        ("bottom_right",         "show_purpose_bottom_right"),
        ("top_left",              "show_need_top_left"),
        ("top_right",             "show_need_top_right_name"),
        ("bottom_left",          "show_need_bottom_left_name"),
        ("bottom_right",         "show_need_bottom_right_name"),
    )

    def _slot_transform(rng: random.Random, key: str, *, f_range: tuple[float, float], angle_range: tuple[float, float]) -> str:
        """Inline ``transform`` string for one transformed slot ``key``.

        ``key`` is the quadrant (``top_left`` etc.); the slot centre→origin
        vector sets the pull direction, and ``f`` drawn from ``f_range`` scales
        it; the rotation is drawn from ``angle_range`` (a signed range, so the
        sign is part of the draw — pass a symmetric range like ``(-180, 180)``
        for a full free rotation, or a magnitude+sign pair like ``(2, 5)`` for
        a minimum-magnitude guarantee via the caller). The base centring
        transform (``translateY(±50%)``) is prepended so the inline ``style``
        overrides the CSS ``transform`` without dropping the centring.
        """
        cx, cy = _slot_centres[key]
        vx = axis_x_pct - cx * 100.0
        vy = axis_y_pct - cy * 100.0
        f = rng.uniform(*f_range)
        dx_cqw = f * vx
        # ``cqh`` is unavailable (the container is ``inline-size``); convert the
        # y component to ``cqw`` by multiplying by height/width — the physical
        # y distance is ``vy/100 * height``, and ``cqw = width/100``, so the
        # distance in cqw is ``vy * height/width``. Height < width for the
        # full diagram, so the y pull is smaller in cqw than the x pull
        # (matching the smaller physical extent), not larger.
        dy_cqw = f * vy * _height_over_width
        angle = rng.uniform(*angle_range)
        base = _slot_base_transform[key]
        return (
            f"{base} translate({dx_cqw:.4f}cqw, {dy_cqw:.4f}cqw) "
            f"rotate({angle:.4f}deg)"
        )

    # ``blur``: a gentle jitter — small inward pull, small rotation across a
    # signed range (any angle from -5° to +5°, including near-zero).
    _BLUR_F_RANGE = (0.3, 0.5)
    _BLUR_ANGLE_RANGE = (-3.0, 3.0)

    def _blur_transform(rng: random.Random, key: str) -> str:
        return _slot_transform(
            rng, key,
            f_range=_BLUR_F_RANGE,
            angle_range=_BLUR_ANGLE_RANGE,
        )

    # ``collapse``: a dramatic, full-structure collapse — strong inward pull
    # (slots can overlap) and a free rotation across the full signed range
    # (any angle, including near-zero and ±180°). The pull is a large fraction
    # of the slot→origin distance so slots are dragged firmly toward the
    # centre; the rotation is unconstrained, so slots can end up sideways or
    # upside down. The signed range is cleaner than magnitude+sign here
    # because "any angle" includes the small angles that form would exclude,
    # and there is no minimum-magnitude guarantee to preserve.
    _COLLAPSE_F_RANGE = (0.7, 1.0)
    _COLLAPSE_ANGLE_RANGE = (-180.0, 180.0)

    def _collapse_transform(rng: random.Random, key: str) -> str:
        return _slot_transform(
            rng, key,
            f_range=_COLLAPSE_F_RANGE,
            angle_range=_COLLAPSE_ANGLE_RANGE,
        )

    # One draw shared between default and alt when both are present (same
    # random values for both states): the same per-slot transform is used to
    # fill both ``blur_default_transforms`` and ``blur_alt_transforms`` so the
    # unhovered (default) and hovered (alt) blurred spans land in the same
    # spot. ``blur-alt`` alone gets its own draw (its own values);
    # ``blur-both`` is its own draw (always applied). The generator is
    # unseeded: the blur is meant to reshuffle on every build, so OS
    # entropy is used (tests assert structure, not values — see the
    # ``_diagram_id_counter`` note above).
    rng = random.Random()
    # Always populate all 12 keys in each dict so StrictUndefined doesn't raise
    # on the template's ``blur_default_transforms[show_flag]`` lookup; the
    # empty string renders as no ``style`` attribute (the template tests
    # ``blur_default_transforms[flag]`` for truthiness before emitting it).
    blur_default_transforms: dict[str, str] = {flag: "" for _, flag in _slot_flag_names}
    blur_alt_transforms: dict[str, str] = {flag: "" for _, flag in _slot_flag_names}
    blur_both_transforms: dict[str, str] = {flag: "" for _, flag in _slot_flag_names}
    collapse_default_transforms: dict[str, str] = {flag: "" for _, flag in _slot_flag_names}
    collapse_alt_transforms: dict[str, str] = {flag: "" for _, flag in _slot_flag_names}
    collapse_both_transforms: dict[str, str] = {flag: "" for _, flag in _slot_flag_names}
    if blur_default or blur_alt:
        # One draw per slot shared between default and alt: the same transform
        # string is assigned to both dicts' entries for that slot's flag.
        draw = {flag: _blur_transform(rng, key) for key, flag in _slot_flag_names}
        for key, flag in _slot_flag_names:
            t = draw[flag]
            if blur_default:
                blur_default_transforms[flag] = t
            if blur_alt:
                blur_alt_transforms[flag] = t
    if blur_both:
        for key, flag in _slot_flag_names:
            blur_both_transforms[flag] = _blur_transform(rng, key)
    # ``collapse`` mirrors ``blur``: one draw shared between default and alt
    # when both are present; ``collapse-both`` is its own draw. ``collapse``'s
    # draw is independent of ``blur``'s (separate per-slot random values), so
    # the two effects compose only at the template level (see the template's
    # ``elif`` chain — ``collapse`` wins over ``blur`` when both target the
    # same span, since the collapse is the more dramatic effect).
    if collapse_default or collapse_alt:
        draw = {flag: _collapse_transform(rng, key) for key, flag in _slot_flag_names}
        for key, flag in _slot_flag_names:
            t = draw[flag]
            if collapse_default:
                collapse_default_transforms[flag] = t
            if collapse_alt:
                collapse_alt_transforms[flag] = t
    if collapse_both:
        for key, flag in _slot_flag_names:
            collapse_both_transforms[flag] = _collapse_transform(rng, key)

    show_advert = (
        any(name.endswith("-alt") for name in labels)
        or bool(top_alt or bottom_alt or left_alt or right_alt)
        or has_axis_alt
        or blur_alt
        or collapse_alt
    )
    # ``-both`` never fires the advert cue: a ``-both``-only diagram has no
    # hover interaction (the ``-both`` labels are always visible, plain). The
    # cue signals "this diagram has a hover-revealed variant", which only the
    # ``-alt`` family provides.

    # Label-swap trigger (global within labels): any label ``-alt`` or any
    # half-annotation ``-alt`` makes ALL default (no-suffix) labels
    # ``label-swappable`` (fade out on hover) so the ``-alt`` labels take their
    # place. This mirrors how axis-line swap works (any axis-line ``-alt`` =>
    # all default axis lines fade) but is independent of it: an axis-line
    # ``-alt`` alone does NOT make labels swap, and a label ``-alt`` alone does
    # NOT make axis lines swap. ``-both`` labels are never swappable.
    label_swap_active = bool(
        any(name.endswith("-alt") for name in labels)
        or top_alt or bottom_alt or left_alt or right_alt
        or blur_alt
    )

    # Axis-line visibility from the directive args. ``x-axis`` / ``y-axis`` /
    # ``axes`` (without a suffix) are the default lines; the same with ``-alt``
    # are the hover-revealed variants (rendered with ``label-alt``); the same
    # with ``-both`` are always visible (plain, no swap classes). When any
    # axis-line ``-alt`` is present, the default lines become
    # ``label-swappable`` (fade out on hover) so the alt lines take their
    # place. With no axis-related args at all, no axis lines are shown.
    # ``-both`` does NOT wire a swap.
    show_x_axis = ("axes" in categories_default) or ("x-axis" in categories_default)
    show_y_axis = ("axes" in categories_default) or ("y-axis" in categories_default)
    show_x_axis_alt = ("axes" in categories_alt) or ("x-axis" in categories_alt)
    show_y_axis_alt = ("axes" in categories_alt) or ("y-axis" in categories_alt)
    show_x_axis_both = ("axes" in categories_both) or ("x-axis" in categories_both)
    show_y_axis_both = ("axes" in categories_both) or ("y-axis" in categories_both)
    # A default axis line is swappable only when an axis-line -alt variant
    # exists anywhere in the directive, so e.g. ``x-axis y-axis-alt`` shows x
    # unhovered and y hovered (x fades out, y fades in).
    x_axis_swappable = show_x_axis and has_axis_alt
    y_axis_swappable = show_y_axis and has_axis_alt

    context = {
        "diagram_id": diagram_id,
        "user_classes": user_classes,
        "variant": geometry["variant"],
        "y_axis_mode": y_axis_mode,
        "axis_high": geometry["axis_high"],
        "axis_low": geometry["axis_low"],
        # Grid geometry + CSS variables (all pre-formatted strings).
        "grid_cols": geometry["grid_cols"],
        "grid_rows": geometry["grid_rows"],
        "aspect_ratio": geometry["aspect_ratio"],
        "axis_x_pos": geometry["axis_x_pos"],
        "axis_y_pos": geometry["axis_y_pos"],
        "central_row": geometry["central_row"],
        "type_x_pct": geometry["type_x_pct"],
        "type_y_pct": geometry["type_y_pct"],
        "purpose_x_pct": geometry["purpose_x_pct"],
        "axis_x_label_pct": geometry["axis_x_label_pct"],
        "axis_y_label_pct": geometry["axis_y_label_pct"],
        "type_font": geometry["type_font"],
        "purpose_font": geometry["purpose_font"],
        "axis_font": geometry["axis_font"],
        "need_font": geometry["need_font"],
        "annotation_font": annotation_font,
        "axis_stroke": geometry["axis_stroke"],
        "guide_v_left": geometry["guide_v_left"],
        "guide_v_right": geometry["guide_v_right"],
        "guide_h_top": geometry["guide_h_top"],
        "guide_h_bottom": geometry["guide_h_bottom"],
        "guide_stroke": geometry["guide_stroke"],
        "cue_size": geometry["cue_size"],
        "cue_border": geometry["cue_border"],
        "cue_dot": geometry["cue_dot"],
        "cue_inset": geometry["cue_inset"],
        "purpose_ls": geometry["purpose_ls"],
        "title": title,
        "desc": desc,
        "show_advert": show_advert,
        # Blur transforms (per-slot ``transform`` strings for the 12 quadrant
        # content labels): empty dict when the corresponding ``blur`` variant
        # is absent, so the template's ``blur_default_transforms[show_flag]``
        # lookup returns ``Undefined`` (no ``style`` attribute emitted). Always
        # set the three dict vars so StrictUndefined is happy even when blur is
        # inactive.
        "blur_default_transforms": blur_default_transforms,
        "blur_alt_transforms": blur_alt_transforms,
        "blur_both_transforms": blur_both_transforms,
        # Collapse transforms: same shape as blur, but the more dramatic effect
        # (strong inward pull, free rotation). When both ``blur`` and
        # ``collapse`` target the same span the template's ``elif`` chain lets
        # ``collapse`` win (it is the more dramatic effect).
        "collapse_default_transforms": collapse_default_transforms,
        "collapse_alt_transforms": collapse_alt_transforms,
        "collapse_both_transforms": collapse_both_transforms,
        # `guides` (bool): render construction guide lines (frame + the
        # purpose-edge cross) when true. Resolved from conf.py typography.
        # `guides` in conf.py is a dict `{"show": bool, "x": int, "y": int}`;
        # only `show` gates the rendering here. The x/y offsets are consumed
        # inside `_html_geometry` (passed through above) and have no separate
        # use in the template. A non-empty dict is always truthy, so read
        # `show` explicitly rather than coercing the dict to bool.
        "guides": bool(guides_cfg.get("show", False)),
        # Label-swap trigger (global within labels): any label ``-alt`` or any
        # half-annotation ``-alt`` makes all default labels swappable. ``-both``
        # labels are never swappable. Independent of the axis-line swap.
        "label_swap_active": label_swap_active,
        # Axis-line visibility (see the variables computed above the context).
        "show_x_axis": show_x_axis,
        "show_y_axis": show_y_axis,
        "show_x_axis_alt": show_x_axis_alt,
        "show_y_axis_alt": show_y_axis_alt,
        "show_x_axis_both": show_x_axis_both,
        "show_y_axis_both": show_y_axis_both,
        "x_axis_swappable": x_axis_swappable,
        "y_axis_swappable": y_axis_swappable,
        "show_axis_label_top": ("top-left" in quadrants or "top-right" in quadrants) and ("axis-label-top" in labels or "axis-label-top-alt" in labels or "axis-label-top-both" in labels),
        "show_axis_label_bottom": ("bottom-left" in quadrants or "bottom-right" in quadrants) and ("axis-label-bottom" in labels or "axis-label-bottom-alt" in labels or "axis-label-bottom-both" in labels),
        "show_axis_label_left": ("top-left" in quadrants or "bottom-left" in quadrants) and ("axis-label-left" in labels or "axis-label-left-alt" in labels or "axis-label-left-both" in labels),
        "show_axis_label_right": ("top-right" in quadrants or "bottom-right" in quadrants) and ("axis-label-right" in labels or "axis-label-right-alt" in labels or "axis-label-right-both" in labels),
        "show_name_top_left": "top-left" in quadrants and ("name-top-left" in labels or "name-top-left-alt" in labels or "name-top-left-both" in labels),
        "show_name_top_right": "top-right" in quadrants and ("name-top-right" in labels or "name-top-right-alt" in labels or "name-top-right-both" in labels),
        "show_name_bottom_right": "bottom-right" in quadrants and ("name-bottom-right" in labels or "name-bottom-right-alt" in labels or "name-bottom-right-both" in labels),
        "show_name_bottom_left": "bottom-left" in quadrants and ("name-bottom-left" in labels or "name-bottom-left-alt" in labels or "name-bottom-left-both" in labels),
        "show_purpose_top_left": "top-left" in quadrants and ("purpose-top-left" in labels or "purpose-top-left-alt" in labels or "purpose-top-left-both" in labels),
        "show_purpose_top_right": "top-right" in quadrants and ("purpose-top-right" in labels or "purpose-top-right-alt" in labels or "purpose-top-right-both" in labels),
        "show_purpose_bottom_right": "bottom-right" in quadrants and ("purpose-bottom-right" in labels or "purpose-bottom-right-alt" in labels or "purpose-bottom-right-both" in labels),
        "show_purpose_bottom_left": "bottom-left" in quadrants and ("purpose-bottom-left" in labels or "purpose-bottom-left-alt" in labels or "purpose-bottom-left-both" in labels),
        "show_need_top_left": "top-left" in quadrants and ("need-top-left" in labels or "need-top-left-alt" in labels or "need-top-left-both" in labels),
        "show_need_top_right_name": "top-right" in quadrants and ("need-top-right-name" in labels or "need-top-right-name-alt" in labels or "need-top-right-name-both" in labels),
        "show_need_bottom_right_name": "bottom-right" in quadrants and ("need-bottom-right-name" in labels or "need-bottom-right-name-alt" in labels or "need-bottom-right-name-both" in labels),
        "show_need_bottom_left_name": "bottom-left" in quadrants and ("need-bottom-left-name" in labels or "need-bottom-left-name-alt" in labels or "need-bottom-left-name-both" in labels),
        # Multiline annotation labels (may be empty lists; the template gates
        # each block on truthiness). Always set so StrictUndefined is happy.
        "top_half": top,
        "bottom_half": bottom,
        "left_half": left,
        "right_half": right,
        "top_half_alt": top_alt,
        "bottom_half_alt": bottom_alt,
        "left_half_alt": left_alt,
        "right_half_alt": right_alt,
        "top_half_both": top_both,
        "bottom_half_both": bottom_both,
        "left_half_both": left_both,
        "right_half_both": right_both,
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
        jinja2.Environment(
            autoescape=True,
            undefined=jinja2.StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
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
