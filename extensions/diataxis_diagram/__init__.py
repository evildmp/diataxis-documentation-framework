"""
Sphinx extension rendering the Diátaxis map diagram.

Labels from the directive's content block (``:name: value`` lines) and the
required ``:title:`` / ``:desc:`` options are stored as translatable
``nodes.inline`` children so ``make gettext`` extracts them; a transform
copies the (translated) label nodes back onto the node before HTML
rendering. Content labels are parsed as inline RST, so ``*emphasis*`` and
``**strong**`` render as markup; ``title``/``desc`` stay plain (aria-label).
Label ids are hyphenated in RST but underscored in the template context
(Jinja2 identifiers cannot contain hyphens).
"""

from __future__ import annotations

import re
import math
import random
from pathlib import Path

import jinja2
import markupsafe
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.transforms import Transform

from sphinx.errors import ExtensionError


# Uniqueness holds within a page (one doctree, one process), even though the
# counter persists across builds in the same process; tests assert structure,
# not id values.
DIAGRAM_ID_COUNTER = 0


def next_diagram_id() -> str:
    global DIAGRAM_ID_COUNTER
    DIAGRAM_ID_COUNTER += 1
    return f"diataxis-diagram-{DIAGRAM_ID_COUNTER}"


# Order matches the historical hand-listed LABEL_NAMES order (bottom-right
# before bottom-left); changing it changes label generation order.
QUADRANT_KEYS = ("top-left", "top-right", "bottom-right", "bottom-left")
CONTENT_KINDS = ("name", "purpose", "need")
LABEL_SUFFIXES = ("", "-alt", "-both")
def content_label_base(kind: str, quadrant: str) -> str:
    """Label base token (no suffix) for one (kind, quadrant) content slot."""
    return f"{kind}-{quadrant}"


# Template CSS class token per content kind (label kind ``name`` renders
# with the ``type`` class).
CSS_KIND_TOKENS = {"name": "type", "purpose": "purpose", "need": "need"}

# Differs from QUADRANT_KEYS; preserving it keeps the RNG draw order for
# per-slot transforms unchanged.
SLOT_QUADRANT_ORDER = ("top-left", "top-right", "bottom-left", "bottom-right")
CONTENT_SLOT_FLAGS = tuple(
    (quadrant.replace("-", "_"),
     f"show_{content_label_base(kind, quadrant).replace('-', '_')}")
    for kind in CONTENT_KINDS
    for quadrant in SLOT_QUADRANT_ORDER
)


# ``-alt`` labels are hover-revealed, ``-both`` always visible (see
# technical-guide.rst).
QUADRANT_CONTENT_LABELS = {
    kind: tuple(
        f"{content_label_base(kind, quadrant)}{suffix}"
        for quadrant in QUADRANT_KEYS
        for suffix in LABEL_SUFFIXES
    )
    for kind in CONTENT_KINDS
}
LABEL_NAMES = (
    *QUADRANT_CONTENT_LABELS["name"],
    *QUADRANT_CONTENT_LABELS["purpose"],
    *(f"axis-label-{side}{suffix}"
      for side in ("left", "right", "top", "bottom")
      for suffix in LABEL_SUFFIXES),
    *(f"{half}-half{suffix}"
      for half in ("top", "bottom", "left", "right")
      for suffix in LABEL_SUFFIXES),
    *QUADRANT_CONTENT_LABELS["need"],
)
# Each list item is stored as its own translatable node with a
# ``<name>-<index>`` field key, re-collected into an ordered list at render
# time.
MULTILINE_LABELS = (
    "top-half", "bottom-half", "left-half", "right-half",
    "top-half-alt", "bottom-half-alt", "left-half-alt", "right-half-alt",
    "top-half-both", "bottom-half-both", "left-half-both", "right-half-both",
)
AXIS_LINE_ARGS = ("axes", "x-axis", "y-axis")
# Must be pulled out of ``quadrants`` before the unknown-arg check (see
# ``run``).
FLAG_ARGS = ("blur", "collapse")
QUADRANTS = ("top-left", "top-right", "bottom-left", "bottom-right")
QUADRANT_SIDES = {
    "top-left":     ("left",   "top"),
    "top-right":    ("right",  "top"),
    "bottom-left":  ("left",   "bottom"),
    "bottom-right": ("right",  "bottom"),
}
LABEL_RE = re.compile(r"^:([a-z-]+):\s*(.*)$")

# Resolution order: these defaults, then conf.py's ``default`` key, then the
# per-locale entry (see on_html_visit_diataxis_diagram).
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


def merge_typography_layer(base: dict, overlay: dict) -> dict:
    """Deep-merge ``overlay`` onto ``base``; nested dicts merge per-key."""
    result = {k: dict(v) if isinstance(v, dict) else v for k, v in base.items()}
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(result.get(k), dict):
            result[k] = merge_typography_layer(result[k], v)
        else:
            result[k] = v
    return result


def strip_quotes(value: str) -> str:
    """Strip one layer of surrounding quotes; whitespace inside is preserved."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value


def split_csv(value: str) -> list[str]:
    """Split on commas that are not inside surrounding quotes.

    A quote character (single or double) opens a quoted span that runs until
    the next matching quote of the same kind; commas inside the span are
    preserved and do not split. The quotes themselves are kept in the output
    and stripped per part by ``strip_quotes``. Unquoted commas split as
    before, so ``a, b, c`` yields ``['a', ' b', ' c']`` (whitespace trimmed by
    ``strip_quotes``), while ``"Hello, world", "L2"`` yields
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


FULL_HALF_W = 960
FULL_HALF_H = 540


def variant_name(quadrants) -> str:
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


def compute_html_geometry(quadrants, font_sizes, offsets, guides):
    """Compute the HTML grid geometry and CSS variables for the selection.

    The diagram is a CSS grid: two columns (left/right of the y-axis), two or
    three rows (top quadrants / central axis band / bottom quadrants). Each
    side is either the full half-extent (960 / 540) or a stub of
    ``2 * axis_font_size`` past the origin. Returns strings for the template's
    inline style; font sizes are in ``cqw`` so the diagram scales with its
    container.
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

    # Track sizes in canvas px (each side is full or stub).
    left_w = FULL_HALF_W if has_left else pad
    right_w = FULL_HALF_W if has_right else pad
    quad_h = FULL_HALF_H - central_half          # a full quadrant row height
    top_row_h = quad_h if has_top else 0
    bottom_row_h = quad_h if has_bottom else 0
    central_h = (central_half if has_top else pad) + (central_half if has_bottom else pad)

    width = left_w + right_w
    height = top_row_h + central_h + bottom_row_h

    if left_w == right_w:
        grid_cols = "1fr 1fr"
    else:
        grid_cols = f"{left_w / width * 100:.4f}% {right_w / width * 100:.4f}%"

    row_sizes = [s for s in (top_row_h, central_h, bottom_row_h) if s]
    grid_rows = " ".join(f"{s / height * 100:.4f}%" for s in row_sizes)

    # Last row for ``top*`` variants, first for ``bottom*``, else middle.
    if has_top and has_bottom:
        central_row = 2
    elif has_top:
        central_row = 2
    else:
        central_row = 1

    # Axis position as % of the visible region (distance from the visible
    # edge to the origin).
    axis_x_pos = (FULL_HALF_W if has_left else pad) / width * 100
    axis_y_pos = ((quad_h + central_half) if has_top else pad) / height * 100
    axis_high = axis_y_pos > 50
    axis_low = axis_y_pos < 50

    # Guide lines at +/-guides_x / +/-guides_y from the axes; % of the
    # visible region. Off-region guides are clipped by `overflow: hidden`.
    guide_v_left = axis_x_pos - guides_x / width * 100
    guide_v_right = axis_x_pos + guides_x / width * 100
    guide_h_top = axis_y_pos - guides_y / height * 100
    guide_h_bottom = axis_y_pos + guides_y / height * 100

    # Annotation anchors. Left/right sit on the vertical guide positions.
    # Top/bottom are vertically centred between the axis (origin) and the
    # near edge of the diagram. Only meaningful for sides that exist
    # (blocks for an absent half are never rendered).
    annotation_left_x = guide_v_left
    annotation_right_x = guide_v_right
    annotation_top_y = axis_y_pos / 2
    annotation_bottom_y = (axis_y_pos + 100) / 2

    gcd = math.gcd(round(width), round(height))
    aspect_ratio = f"{round(width) // gcd} / {round(height) // gcd}"

    def cqw(px):
        return f"{px / width * 100:.4f}cqw"

    def pct(v):
        return f"{v:.4f}%"

    return {
        "variant": variant_name(quadrants),
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
        "type_font": cqw(font_sizes["type"]),
        "purpose_font": cqw(font_sizes["purpose"]),
        "axis_font": cqw(font_sizes["axis"]),
        "need_font": cqw(font_sizes["need"]),
        # Denominator is the fixed 960px quadrant width, so constant across
        # variants.
        "type_x_pct": pct(type_x / FULL_HALF_W * 100),
        "purpose_x_pct": pct(type_purpose_x / FULL_HALF_W * 100),
        # Denominator is the per-variant container size (not the fixed half)
        # so it is exact across all variants. The 2× factor accounts for the
        # template's ``/2`` in the calc() consuming this variable.
        "axis_x_label_pct": pct(2 * axis_x / width * 100),
        "axis_y_label_pct": pct(central_half / height * 100),
        # Measured from the inner edge of the quadrant row.
        "type_y_pct": pct((type_y - central_half) / quad_h * 100),
        "axis_stroke": f"max({cqw(2)}, 1px)",
        "guide_v_left": pct(guide_v_left),
        "guide_v_right": pct(guide_v_right),
        "guide_h_top": pct(guide_h_top),
        "guide_h_bottom": pct(guide_h_bottom),
        "guide_stroke": f"max({cqw(1)}, 1px)",
        "annotation_left_x": pct(annotation_left_x),
        "annotation_right_x": pct(annotation_right_x),
        "annotation_top_y": pct(annotation_top_y),
        "annotation_bottom_y": pct(annotation_bottom_y),
        "cue_size": cqw(60),
        "cue_border": cqw(3),
        "cue_dot": cqw(12),
        "cue_inset": cqw(30),
        "purpose_ls": cqw(2.2),
    }


class diataxis_diagram(nodes.General, nodes.Element):
    """Placeholder node resolved by the HTML translator visit/depart."""


def make_label_node(
    name: str,
    value: str,
    source: str,
    line: int,
    children: list[nodes.Node] | None = None,
) -> nodes.inline:
    """Translatable inline node carrying one label's text.

    ``translatable`` is required (plain ``nodes.Inline`` is skipped by
    gettext); ``source``/``line`` are required (sourceless nodes are treated
    as built-in and skipped).

    ``children`` is an optional pre-parsed inline fragment (from
    ``State.inline_text``) — e.g. emphasis/strong — carried inside the node;
    without it the label is plain text.
    """
    node = nodes.inline(value, "")
    node.clear()
    if children:
        node.extend(children)
    else:
        node.append(nodes.Text(value))
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

        # Directive args may carry ``-alt`` (hover-revealed) or ``-both``
        # (always visible) suffixes; the stripped base drives quadrant
        # selection and axis-line visibility. Only ``x-axis`` / ``y-axis`` /
        # ``axes`` gate a swappable element, so the suffixes on other args
        # are no-ops. ``-both`` never wires a swap or fires the advert cue.
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

        quadrants = all_args.difference(AXIS_LINE_ARGS)
        # Flag args are neither quadrants nor axis args; strip them before
        # the unknown-arg check (they are already tracked via the suffix
        # split above).
        quadrants = {q for q in quadrants if q not in FLAG_ARGS}
        if not quadrants:
            quadrants = set(QUADRANTS)
        unknown = quadrants.difference(QUADRANTS)
        if unknown:
            raise ExtensionError(
                f"diataxis-diagram: unknown argument "
                f"{', '.join(sorted(unknown))!r}; "
                f"known quadrants: {', '.join(QUADRANTS)}, "
                f"known axis args: {', '.join(AXIS_LINE_ARGS)}"
            )
        node["quadrants"] = quadrants

        if "title" not in self.options:
            raise ExtensionError("diataxis-diagram: missing required option :title:")
        if "desc" not in self.options:
            raise ExtensionError("diataxis-diagram: missing required option :desc:")
        node += make_label_node("title", self.options["title"], source, self.lineno)
        node += make_label_node("desc", self.options["desc"], source, self.lineno)

        for i, line in enumerate(self.content):
            m = LABEL_RE.match(line)
            if not m:
                continue
            name, value = m.group(1), m.group(2)
            if name not in LABEL_NAMES:
                raise ExtensionError(
                    f"diataxis-diagram: unknown label option :{name}: "
                    f"(known: {', '.join(LABEL_NAMES)})"
                )
            if name in MULTILINE_LABELS:
                parts = [strip_quotes(p) for p in split_csv(value)]
                parts = [p for p in parts if p]
                for j, part in enumerate(parts):
                    parsed, _ = self.state.inline_text(part, self.lineno + i)
                    node += make_label_node(
                        f"{name}-{j}", part, source, self.lineno + i, children=parsed
                    )
            else:
                stripped = strip_quotes(value)
                parsed, _ = self.state.inline_text(stripped, self.lineno + i)
                node += make_label_node(
                    name, stripped, source, self.lineno + i, children=parsed
                )

        return [node]



class CaptureDiataxisDiagramLabels(Transform):
    """Copy translated label nodes from inline children onto the node.

    Runs after ``Locale`` (20) rewrites the inline text and before
    ``RemoveTranslatableInline`` (999) strips the wrappers; without it the
    ``field_key`` association is gone by HTML build time. The inline nodes
    are stored whole (not flattened with ``astext()``) so parsed markup
    (emphasis/strong) inside labels survives to HTML rendering; the HTML
    visitor flattens ``title``/``desc`` and serializes the rest.
    """

    default_priority = 500

    def apply(self, **kwargs):
        for node in self.document.findall(diataxis_diagram):
            labels = {}
            for child in node.children:
                if isinstance(child, nodes.inline) and "field_key" in child:
                    labels[child["field_key"]] = child
            node["labels"] = labels


def render_label_fragment(translator, fragment) -> markupsafe.Markup:
    """Render a parsed inline fragment (Text/emphasis/strong/...) to HTML.

    Uses the live HTML translator so escaping matches the rest of the page;
    the temporary body swap keeps the main output untouched. The result is
    a Jinja-safe Markup so the template's autoescape leaves it intact.
    """
    saved_body = translator.body
    translator.body = []
    try:
        for child in fragment:
            child.walkabout(translator)
        return markupsafe.Markup("".join(translator.body))
    finally:
        translator.body = saved_body


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

    def label_text(value):
        # Labels are stored as translatable inline nodes carrying parsed
        # markup; cached doctrees from older builds may hold plain strings.
        return value.astext() if isinstance(value, nodes.Element) else str(value)

    # aria-label must stay flat text — never markup.
    title = label_text(labels.pop("title", ""))
    desc = label_text(labels.pop("desc", ""))

    # Content labels may carry parsed markup; serialize to HTML now so the
    # template interpolates ready-made Markup. Plain strings (old doctrees)
    # pass through unchanged and are escaped by Jinja as before.
    for key, value in labels.items():
        if isinstance(value, nodes.Element):
            labels[key] = render_label_fragment(self, value.children)

    # Three-layer merge: DEFAULT_TYPOGRAPHY, conf.py ``default`` key,
    # per-locale entry; nested dicts merge per-key.
    typography = env.config.diataxis_diagram or {}
    if env.config.language not in typography:
        raise ExtensionError(
            f"diataxis-diagram: language {env.config.language!r} has no entry in "
            f"diataxis_diagram; add one (see source/conf.py)."
        )
    resolved = merge_typography_layer(DEFAULT_TYPOGRAPHY, typography.get("default", {}))
    resolved = merge_typography_layer(resolved, typography[env.config.language])

    offsets = resolved["offsets"]
    font_sizes = resolved["font-sizes"]

    y_axis_mode = resolved["y-axis-rotation"]
    if y_axis_mode not in ("rotated", "stacked"):
        raise ExtensionError(
            f"diataxis-diagram: diataxis_diagram[{env.config.language!r}] "
            f"has unsupported y-axis-rotation value {y_axis_mode!r}; "
            f"expected 'rotated' or 'stacked'."
        )

    # Backward compat: accept a bare bool (old shape), reading x/y from
    # offsets so old behaviour is reproduced exactly.
    guides_cfg = resolved.get("guides", {})
    if isinstance(guides_cfg, bool):
        guides_cfg = {
            "show": guides_cfg,
            "x": offsets["type-purpose-x"],
            "y": offsets["purpose-y"],
        }
    elif not isinstance(guides_cfg, dict):
        guides_cfg = {"show": False, "x": 154, "y": 120}

    # Scopes this diagram's <style> block and @keyframes name away from any
    # other diagram on the same page.
    diagram_id = next_diagram_id()

    user_classes = " ".join(node.get("classes", []))
    quadrants = set(node.get("quadrants", set(QUADRANTS)))
    # Axis args split by suffix; ``has_axis_alt`` feeds ``show_advert`` (any
    # ``-alt`` enables the hover state; ``-both`` does not).
    default_args = set(node.get("default_args", set()))
    alt_args = set(node.get("alt_args", set()))
    both_args = set(node.get("both_args", set()))
    axis_args_default = default_args.intersection(AXIS_LINE_ARGS)
    axis_args_alt = alt_args.intersection(AXIS_LINE_ARGS)
    axis_args_both = both_args.intersection(AXIS_LINE_ARGS)
    has_axis_alt = bool(axis_args_alt)

    geometry = compute_html_geometry(quadrants, font_sizes, offsets, guides_cfg)

    # Re-collect multiline annotation lines (stored as ``<name>-<index>``
    # field keys) into ordered lists, popping them so the hyphen→underscore
    # context update below does not emit unused vars.
    def collect_lines(prefix):
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

    half_lines = {
        f"{side}{suffix}": collect_lines(f"{side}-half{suffix.replace('_', '-')}")
        for side in ("top", "bottom", "left", "right")
        for suffix in ("", "_alt", "_both")
    }

    # Shrink the annotation font as the tallest block grows (aesthetic
    # tuning; 0.10 and the 1.5 exponent are the knobs).
    max_annotation_lines = max(1, *(len(lines) for lines in half_lines.values()))
    annotation_font_size = font_sizes["annotation"] / (1 + 0.10 * (max_annotation_lines - 1) ** 1.5)
    annotation_font = f"{annotation_font_size / geometry['width'] * 100:.4f}cqw"

    # --- Blur / collapse effects (``blur``/``collapse`` + ``-alt``/``-both``) ---
    # When present, each of the 12 quadrant content slots gets a randomized
    # transform drawn once per slot at build time. ``X`` applies unhovered;
    # ``X-alt`` on hover; ``X-both`` always. ``-alt`` fires the advert cue and
    # contributes to ``label_swap_active``; ``-both`` does neither. Axis
    # labels are never transformed.
    blur_default = "blur" in default_args
    blur_alt = "blur" in alt_args
    blur_both = "blur" in both_args
    collapse_default = "collapse" in default_args
    collapse_alt = "collapse" in alt_args
    collapse_both = "collapse" in both_args
    # Slot centres (% of the visible region); only the pull direction
    # (toward the origin) matters, magnitude is a randomised fraction of the
    # centre→origin distance.
    axis_x_pct = float(geometry["axis_x_pos"].rstrip("%"))
    axis_y_pct = float(geometry["axis_y_pos"].rstrip("%"))
    height_over_width = geometry["height"] / geometry["width"]
    QUADRANT_CENTRES_PCT = {
        "top_left":         (0.25, 0.25),
        "top_right":        (0.75, 0.25),
        "bottom_left":      (0.25, 0.75),
        "bottom_right":     (0.75, 0.75),
    }
    # Base centring transform per quadrant; must be repeated inline because
    # the inline ``style`` transform overrides the CSS one.
    QUADRANT_BASE_TRANSFORM = {
        "top_left":         "translateY(50%)",
        "top_right":        "translateY(50%)",
        "bottom_left":      "translateY(-50%)",
        "bottom_right":     "translateY(-50%)",
    }

    def slot_transform(rng: random.Random, key: str, *, pull_fraction_range: tuple[float, float], rotation_range_deg: tuple[float, float]) -> str:
        """Inline ``transform`` string for one transformed slot.

        Pull direction is the slot centre→origin vector, scaled by
        ``pull_fraction``; rotation is drawn from ``rotation_range_deg``. The
        base centring transform is prepended so the inline ``style`` does not
        drop the centring.
        """
        cx, cy = QUADRANT_CENTRES_PCT[key]
        to_origin_x = axis_x_pct - cx * 100.0
        to_origin_y = axis_y_pct - cy * 100.0
        pull_fraction = rng.uniform(*pull_fraction_range)
        dx_cqw = pull_fraction * to_origin_x
        # ``cqh`` is unavailable (container is ``inline-size``); convert the y
        # component to cqw by multiplying by height/width.
        dy_cqw = pull_fraction * to_origin_y * height_over_width
        angle = rng.uniform(*rotation_range_deg)
        base = QUADRANT_BASE_TRANSFORM[key]
        return (
            f"{base} translate({dx_cqw:.4f}cqw, {dy_cqw:.4f}cqw) "
            f"rotate({angle:.4f}deg)"
        )

    # ``blur``: gentle jitter.
    BLUR_PULL_FRACTION_RANGE = (0.3, 0.5)
    BLUR_ROTATION_RANGE_DEG = (-3.0, 3.0)

    def blur_transform(rng: random.Random, key: str) -> str:
        return slot_transform(
            rng, key,
            pull_fraction_range=BLUR_PULL_FRACTION_RANGE,
            rotation_range_deg=BLUR_ROTATION_RANGE_DEG,
        )

    # ``collapse``: strong inward pull (slots can overlap) and free rotation.
    COLLAPSE_PULL_FRACTION_RANGE = (0.7, 1.0)
    COLLAPSE_ROTATION_RANGE_DEG = (-180.0, 180.0)

    def collapse_transform(rng: random.Random, key: str) -> str:
        return slot_transform(
            rng, key,
            pull_fraction_range=COLLAPSE_PULL_FRACTION_RANGE,
            rotation_range_deg=COLLAPSE_ROTATION_RANGE_DEG,
        )

    # Unseeded: the effect reshuffles on every build; tests assert structure,
    # not values.
    rng = random.Random()
    # All keys populated so StrictUndefined doesn't raise; empty string
    # renders as no ``style`` attribute.
    transforms: dict[tuple[str, str], dict[str, str]] = {
        (effect, variant): {flag: "" for _, flag in CONTENT_SLOT_FLAGS}
        for effect in ("blur", "collapse")
        for variant in ("default", "alt", "both")
    }

    def apply_effect(effect, transform_fn, active_default, active_alt, active_both):
        """Draw and assign one effect's per-slot transforms.

        One draw shared between default and alt when both are present, so the
        unhovered and hovered spans land in the same spot; ``-alt`` alone and
        ``-both`` each get their own draw.
        """
        if active_default or active_alt:
            draw = {flag: transform_fn(rng, key) for key, flag in CONTENT_SLOT_FLAGS}
            for key, flag in CONTENT_SLOT_FLAGS:
                t = draw[flag]
                if active_default:
                    transforms[(effect, "default")][flag] = t
                if active_alt:
                    transforms[(effect, "alt")][flag] = t
        if active_both:
            for key, flag in CONTENT_SLOT_FLAGS:
                transforms[(effect, "both")][flag] = transform_fn(rng, key)

    apply_effect("blur", blur_transform, blur_default, blur_alt, blur_both)
    apply_effect("collapse", collapse_transform, collapse_default, collapse_alt, collapse_both)

    show_advert = (
        any(name.endswith("-alt") for name in labels)
        or any(lines for key, lines in half_lines.items() if key.endswith("_alt"))
        or has_axis_alt
        or blur_alt
        or collapse_alt
    )

    # When the hover state is enabled (any ``-alt`` anywhere — the same
    # condition as ``show_advert``), ALL default elements fade out on hover,
    # even with no ``-alt`` replacement (strict fade-out). ``-both`` never
    # enables the state and never swaps.
    label_swap_active = show_advert

    # Axis-line visibility from the directive args; with no axis args at all,
    # no axis lines are shown.
    def axis_shown(axis_args: set[str], axis: str) -> bool:
        """Whether ``axis`` (or the both-axes shorthand) is in ``axis_args``."""
        return "axes" in axis_args or axis in axis_args

    show_x_axis = axis_shown(axis_args_default, "x-axis")
    show_y_axis = axis_shown(axis_args_default, "y-axis")
    show_x_axis_alt = axis_shown(axis_args_alt, "x-axis")
    show_y_axis_alt = axis_shown(axis_args_alt, "y-axis")
    show_x_axis_both = axis_shown(axis_args_both, "x-axis")
    show_y_axis_both = axis_shown(axis_args_both, "y-axis")
    # A default axis line is swappable whenever the hover state is enabled
    # (any ``-alt`` anywhere), so e.g. ``x-axis y-axis-alt`` shows x unhovered
    # and y hovered (x fades out, y fades in), and ``axes blur-alt`` fades the
    # axis lines out on hover with no replacement (strict fade-out).
    x_axis_swappable = show_x_axis and show_advert
    y_axis_swappable = show_y_axis and show_advert

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
        "annotation_left_x": geometry["annotation_left_x"],
        "annotation_right_x": geometry["annotation_right_x"],
        "annotation_top_y": geometry["annotation_top_y"],
        "annotation_bottom_y": geometry["annotation_bottom_y"],
        "cue_size": geometry["cue_size"],
        "cue_border": geometry["cue_border"],
        "cue_dot": geometry["cue_dot"],
        "cue_inset": geometry["cue_inset"],
        "purpose_ls": geometry["purpose_ls"],
        "title": title,
        "desc": desc,
        "show_advert": show_advert,
        "guides": bool(guides_cfg.get("show", False)),
        "label_swap_active": label_swap_active,
        "show_x_axis": show_x_axis,
        "show_y_axis": show_y_axis,
        "show_x_axis_alt": show_x_axis_alt,
        "show_y_axis_alt": show_y_axis_alt,
        "show_x_axis_both": show_x_axis_both,
        "show_y_axis_both": show_y_axis_both,
        "x_axis_swappable": x_axis_swappable,
        "y_axis_swappable": y_axis_swappable,
        # An axis label shows when either flanking quadrant is selected and
        # any suffix variant exists; a content slot likewise.
        **{
            f"show_axis_label_{side}": (
                any(q in quadrants for q in flank_quadrants)
                and any(f"axis-label-{side}{s}" in labels for s in LABEL_SUFFIXES)
            )
            for side, flank_quadrants in {
                "top": ("top-left", "top-right"),
                "bottom": ("bottom-left", "bottom-right"),
                "left": ("top-left", "bottom-left"),
                "right": ("top-right", "bottom-right"),
            }.items()
        },
        **{
            f"show_{content_label_base(kind, q).replace('-', '_')}": (
                q in quadrants
                and any(
                    f"{content_label_base(kind, q)}{suffix}" in labels
                    for suffix in LABEL_SUFFIXES
                )
            )
            for kind in CONTENT_KINDS
            for q in QUADRANT_KEYS
        },
        # May be empty lists; always set so StrictUndefined is happy.
        **{
            f"{side}_half{suffix}": half_lines[f"{side}{suffix}"]
            for side in ("top", "bottom", "left", "right")
            for suffix in ("", "_alt", "_both")
        },
    }
    # Default all scalar label values to "" so the template's {% if %} gates
    # work under StrictUndefined even when only an -alt variant is present.
    context.update({
        name.replace("-", "_"): ""
        for name in LABEL_NAMES
        if name not in MULTILINE_LABELS
    })
    context.update({k.replace("-", "_"): v for k, v in labels.items()})

    # Transform-priority chain (collapse > blur; ``-both`` fallbacks last)
    # resolved once here instead of per-slot in Jinja.
    def resolve_transform(*candidates: str) -> str:
        """First non-empty candidate, or empty string if none."""
        return next((t for t in candidates if t), "")

    content_slots = []
    for kind in CONTENT_KINDS:
        for quadrant in SLOT_QUADRANT_ORDER:
            base = content_label_base(kind, quadrant)
            var = base.replace("-", "_")
            flag = f"show_{var}"
            content_slots.append({
                "kind": kind,
                "css": CSS_KIND_TOKENS[kind],
                "quadrant": quadrant,
                "show": context[flag],
                "labels": {
                    "default": context[var],
                    "alt": context[f"{var}_alt"],
                    "both": context[f"{var}_both"],
                },
                "default_transform": resolve_transform(
                    transforms[("collapse", "default")][flag],
                    transforms[("blur", "default")][flag],
                    transforms[("blur", "both")][flag],
                    transforms[("collapse", "both")][flag],
                ),
                "alt_transform": resolve_transform(
                    transforms[("collapse", "alt")][flag],
                    transforms[("blur", "alt")][flag],
                    # ``-both`` applies in the hovered state too: when the alt
                    # has no transform of its own, fall back to ``-both``
                    # (mirroring the default chain's order).
                    transforms[("blur", "both")][flag],
                    transforms[("collapse", "both")][flag],
                ),
                # The always-shown ``-both`` span carries the ``-both``
                # transform in both states.
                "both_transform": resolve_transform(
                    transforms[("blur", "both")][flag],
                    transforms[("collapse", "both")][flag],
                ),
            })
    context["content_slots"] = content_slots

    annotation_positions = {
        "top": "left: 50%; top: var(--annotation-top-y)",
        "bottom": "left: 50%; top: var(--annotation-bottom-y)",
        "left": "left: var(--annotation-left-x); top: 50%",
        "right": "left: var(--annotation-right-x); top: 50%",
    }
    context["annotation_blocks"] = [
        {
            "side": side,
            "suffix": suffix,
            "lines": half_lines[f"{side}{suffix}"],
            "position": annotation_positions[side],
        }
        for side in ("top", "bottom", "left", "right")
        for suffix in ("", "_alt", "_both")
    ]
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
    app.add_transform(CaptureDiataxisDiagramLabels)
    static_dir = str(Path(__file__).resolve().parent / "static")
    app.connect("builder-inited",
                lambda app: app.config.html_static_path.append(static_dir))
    app.add_css_file("diataxis-diagram.css")
    return {"parallel_read_safe": True, "parallel_write_safe": True}
