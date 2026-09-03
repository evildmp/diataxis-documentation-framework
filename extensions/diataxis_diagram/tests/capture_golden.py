"""Capture golden rendered-HTML blocks for byte-diff regression checking.

Renders a deliberate cross-section of ``.. diataxis-diagram::`` invocations
(the 13 cases enumerated in IMPROVEMENT_PLAN.md item 5's regression-safety
procedure) through the same Sphinx build path the test suite uses
(``conftest._build_html`` + ``conftest._diagram_blocks``), and writes each
rendered diagram block to ``tests/golden/<case>.html``.

Usage::

    python tests/capture_golden.py [output-dir]

With no argument the output goes to ``tests/golden/`` (the committed
baseline); pass e.g. ``tests/golden-new/`` to capture a candidate run for
diffing against the baseline with ``diff -r``.

Determinism: the visitor draws blur/collapse transforms from an unseeded
``random.Random()`` (real builds are meant to reshuffle every time). Golden
files must be byte-comparable across runs, so this script pins the RNG by
substituting a fixed-seed ``random.Random`` subclass into the extension
module *before any build*. This affects only golden capture — the test suite
and real builds keep OS-entropy seeding. Because the visitor constructs a
fresh ``Random`` per diagram, every diagram is drawn from the same seed; that
is fine for diffing purposes (same seed in, same values out, every run).
"""

from __future__ import annotations

import random
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import extensions.diataxis_diagram as ext  # noqa: E402

SEED = 0xD1A71A515


class _SeededRandom(random.Random):
    """``random.Random`` pinned to SEED, substituted into the extension."""

    def __init__(self, *args, **kwargs):
        super().__init__(SEED)


ext.random.Random = _SeededRandom

from extensions.diataxis_diagram.tests.conftest import (  # noqa: E402
    DESC_TEXT,
    LABEL_VALUES,
    TITLE_TEXT,
    _build_html,
    _diagram_blocks,
)

DEFAULT_TYPOGRAPHY = {
    "en": {
        "font-sizes": {"type": 104, "purpose": 44, "axis": 44},
        "offsets": {"axis-y": 119},
    }
}
GUIDES_TYPOGRAPHY = {
    **DEFAULT_TYPOGRAPHY,
    "default": {"guides": {"show": True, "x": 154, "y": 120}},
}


def make_rst(args: str = "", extra_labels: dict | None = None) -> str:
    """One directive block with the base 12 labels plus any extras."""
    labels = {**LABEL_VALUES, **(extra_labels or {})}
    label_lines = "\n   ".join(f':{name}: "{value}"' for name, value in labels.items())
    arg_part = f"   {args}\n" if args else ""
    return (
        "Welcome\n"
        "=======\n"
        "\n"
        "..  diataxis-diagram::\n"
        f"{arg_part}"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        f"   {label_lines}\n"
    )


def two_diagram_rst() -> str:
    """Two diagrams on one page (mirrors test_instance_scoping's fixture)."""
    return (
        "Welcome\n"
        "=======\n"
        "\n"
        "..  diataxis-diagram::\n"
        f"   :title: {TITLE_TEXT}\n"
        f"   :desc: {DESC_TEXT}\n"
        "\n"
        + "\n".join(f'   :{name}: "{value}"' for name, value in LABEL_VALUES.items())
        + "\n\n"
        "Some intervening text.\n\n"
        "..  diataxis-diagram::\n"
        f"   :title: Second {TITLE_TEXT}\n"
        f"   :desc: Second {DESC_TEXT}\n"
        "\n"
        + "\n".join(f'   :{name}: "{value}"' for name, value in LABEL_VALUES.items())
        + "\n"
    )


# (case name, directive args, extra labels, typography override)
CASES = [
    ("01-full", "", None, None),
    ("02-quadrant-top-left", "top-left", None, None),
    ("02-quadrant-top-right", "top-right", None, None),
    ("02-quadrant-bottom-left", "bottom-left", None, None),
    ("02-quadrant-bottom-right", "bottom-right", None, None),
    ("03-half-top", "top-left top-right", None, None),
    ("03-half-bottom", "bottom-left bottom-right", None, None),
    ("03-half-left", "top-left bottom-left", None, None),
    ("03-half-right", "top-right bottom-right", None, None),
    ("04-axes", "axes", None, None),
    ("04-x-axis", "x-axis", None, None),
    ("04-y-axis", "y-axis", None, None),
    ("05-x-axis-alt", "x-axis-alt", None, None),
    ("05-y-axis-alt", "y-axis-alt", None, None),
    ("05-axes-alt", "axes-alt", None, None),
    ("06-x-axis-both", "x-axis-both", None, None),
    ("06-y-axis-both", "y-axis-both", None, None),
    ("06-axes-both", "axes-both", None, None),
    ("07-blur", "blur", None, None),
    ("07-blur-alt", "blur-alt", {"name-top-left-alt": "Tutorials (alt)"}, None),
    ("07-blur-both", "blur-both", None, None),
    ("08-collapse", "collapse", None, None),
    ("08-collapse-alt", "collapse-alt", {"name-top-left-alt": "Tutorials (alt)"}, None),
    ("08-collapse-both", "collapse-both", None, None),
    ("09-blur-collapse", "blur collapse", None, None),
    (
        "10-default-alt-both-labels",
        "",
        {
            "name-top-left-alt": "Tutorials (alt)",
            "name-top-left-both": "Tutorials (both)",
        },
        None,
    ),
    ("11-guides-on", "", None, GUIDES_TYPOGRAPHY),
    ("12-advert-cue", "", {"name-top-left-alt": "Tutorials (alt)"}, None),
]


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "golden"
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, args, extra_labels, typography in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            out = _build_html(Path(tmp), make_rst(args, extra_labels), typography=typography)
            html = (out / "index.html").read_text(encoding="utf-8")
        blocks = _diagram_blocks(html)
        assert len(blocks) == 1, f"{name}: expected 1 diagram block, got {len(blocks)}"
        (out_dir / f"{name}.html").write_text(blocks[0], encoding="utf-8")
        print(f"captured {name}.html ({len(blocks[0])} bytes)")

    # Case 13: two diagrams on one page — both blocks in one file.
    with tempfile.TemporaryDirectory() as tmp:
        out = _build_html(Path(tmp), two_diagram_rst())
        html = (out / "index.html").read_text(encoding="utf-8")
    blocks = _diagram_blocks(html)
    assert len(blocks) == 2, f"13-two-diagrams: expected 2 blocks, got {len(blocks)}"
    (out_dir / "13-two-diagrams.html").write_text(
        blocks[0] + "\n<!-- second diagram -->\n" + blocks[1], encoding="utf-8"
    )
    print(f"captured 13-two-diagrams.html (2 blocks)")

    print(f"\n{len(CASES) + 1} golden files written to {out_dir}")


if __name__ == "__main__":
    main()
