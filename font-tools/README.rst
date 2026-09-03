font-tools
==========

Tooling for rebuilding and validating the embedded Skia subset that the
Diátaxis diagram uses (``_static/skia-subset.woff2``).

These scripts are **not** part of the documentation build. They are only
needed when the subset must be rebuilt (e.g. translators add characters
the subset doesn't cover, or the system font is updated) or when
investigating a font-rendering regression. Nothing here is imported by
the site or the ``diataxis_diagram`` extension.

Prerequisites
-------------

- macOS. The scripts read the system font from
  ``/System/Library/Fonts/Supplemental/Skia.ttf``.
- A Python environment with ``fonttools`` and ``brotli``. Pin the
  versions used to build the current subset:

.. code-block:: sh

   pip install -r font-tools/requirements.dev

All scripts assume they are run from the **repository root**, not from
inside ``font-tools/``. Paths like ``_static/skia-subset.woff2`` and
``translation/`` are relative to the repo root.

The subset
----------

``_static/skia-subset.woff2`` is a subset of Apple's Skia variable font,
covering:

- Basic Latin (U+0020–007F)
- Latin-1 Supplement (U+00A0–00FF) — accents for fr/it/de/pt_BR
- Latin Extended-A (U+0100–017F) — Polish ą ć ę ł ń ó ś ź ż and uppercase
- Apostrophes U+0027 (straight) and U+2019 (typographic)
- A few punctuation marks (U+2014 em dash, U+2018–201F quotes)

The ``wdth`` axis is **pinned to 1.0** during the build (see
``build_subset.sh``). The diagram only ever uses ``wdth=1.0``, so
pinning it drops the ``wdth`` axis from ``fvar`` and prunes all
``wdth``-bearing tuples from ``gvar`` — roughly six of the eight
per-glyph variation tuples, halving ``gvar`` size while keeping the
``wght`` axis the diagram actually uses (0.6, 1.0, 1.25).

The ``wght`` axis and its ``gvar`` deltas are kept intact, so
``font-variation-settings: "wght" ...`` still works in the browser.

When to rebuild
---------------

Rebuild the subset when:

- A translator adds a character the subset doesn't cover. Run
  ``scan_po_chars.py`` first to see what's needed.
- The system Skia font is updated (rare).
- You want to investigate a rendering regression in the diagram text.

You do **not** need to rebuild for normal documentation work.

Workflow
--------

A typical rebuild:

.. code-block:: sh

   # 1. See what characters the current translations actually use.
   python3 font-tools/scan_po_chars.py

   # 2. Rebuild the subset (writes _static/skia-subset.woff2).
   font-tools/build_subset.sh

   # 3. Confirm the subset still covers the diagram text and the
   #    translation characters.
   python3 font-tools/inspect_glyphs.py
   python3 font-tools/scan_po_chars.py

   # 4. Confirm the wght variation data still matches the system font
   #    (instanced outline widths at wght=0.48 should match exactly).
   python3 font-tools/check_gvar_coverage.py
   python3 font-tools/check_gvar_axes.py

   # 5. Side-by-side sanity check of axes, name records, gvar summary.
   python3 font-tools/compare_fonts.py

If ``scan_po_chars.py`` reports characters outside the ranges
``build_subset.sh`` currently subsets, edit the ``--unicodes`` argument
in ``build_subset.sh`` to cover them, then rebuild.

Scripts
-------

build_subset.sh
~~~~~~~~~~~~~~~

Rebuilds ``_static/skia-subset.woff2`` from the system Skia font. Runs
``pyftsubset`` for the character subset, then
``instantiateVariableFont`` to pin ``wdth=1.0``, then woff2-compresses
the result. Idempotent: safe to re-run.

scan_po_chars.py
~~~~~~~~~~~~~~~~

Scans every ``.po`` file under ``translation/`` and reports the
non-ASCII characters used in translated (``msgstr``) strings, per
locale and overall. Run this before rebuilding to confirm the subset's
character set covers what translators have actually used.

inspect_glyphs.py
~~~~~~~~~~~~~~~~~

Lists every glyph and cmap entry in the embedded subset, and checks
coverage for the actual rendered diagram text (quadrant labels
uppercased, plus axis/purpose labels in mixed case). Use this to
confirm a rebuild didn't drop a needed glyph.

check_gvar_coverage.py
~~~~~~~~~~~~~~~~~~~~~~

Checks that the glyphs used in the quadrant labels have ``gvar``
``wght`` deltas in the subset, and that instancing the subset at
``wght=0.48`` produces the same outline widths as the system font
instanced the same way. This is the main correctness check after a
rebuild: if widths match, the subset's ``wght`` variation is faithful
to the full font.

check_gvar_axes.py
~~~~~~~~~~~~~~~~~~

Reports which axes (``wght`` vs ``wdth``) the subset's ``gvar`` tuples
actually reference, and measures the ``I`` glyph stem width at
``wght=0.48``, ``1.0``, ``3.2`` to confirm the ``wght`` axis still
drives visible shape change. Use this to confirm ``wdth`` was fully
pruned and ``wght`` was left intact.

inspect_gvar.py
~~~~~~~~~~~~~~~

Dumps the individual ``gvar`` tuples for ``a`` (system) and ``á``
(embedded), showing which axes each tuple references. Useful when
investigating why a glyph has eight tuples in the system font and
fewer in the subset.

compare_fonts.py
~~~~~~~~~~~~~~~~~

Dumps OS/2, fvar, key name records, and a ``gvar`` summary for the
embedded subset and the system font side by side. Use this for a
broad sanity check that the subset preserved the axes and variation
data the diagram relies on.

inspect_embedded.py
~~~~~~~~~~~~~~~~~~~

Dumps the tables, head, OS/2, name records, fvar axes and named
instances, and gvar/HVAR/MVAR/avar presence for the embedded subset.
Use this to confirm the subset is still a variable font with the
``wght`` axis intact.

inspect_skia.py
~~~~~~~~~~~~~~~

Same as ``inspect_embedded.py`` but for the system Skia font. Useful
as the reference when comparing against ``inspect_embedded.py``.

Files referenced
----------------

- ``_static/skia-subset.woff2`` — the subset these scripts build and
  validate. Loaded by ``_static/skia-font.css``, which the site loads
  via ``html_css_files`` in ``conf.py``.
- ``/System/Library/Fonts/Supplemental/Skia.ttf`` — the source system
  font. macOS only.
- ``translation/*/LC_MESSAGES/*.po`` — scanned by ``scan_po_chars.py``
  to determine required character coverage.
