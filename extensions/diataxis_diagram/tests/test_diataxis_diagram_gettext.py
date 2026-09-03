"""Test that ``.. diataxis-diagram::`` label strings are extracted by ``make gettext``.

The directive stores each ``:label-name:`` value as
a translatable ``nodes.inline`` child of the ``diataxis_diagram`` node. Sphinx's
``MessageCatalogBuilder`` should pick all of them up as ``msgid`` entries in
the generated ``.pot``.

This pins the gettext extraction: 12 label values + ``:title:`` +
``:desc:`` = 14 strings.
"""

from __future__ import annotations

import re
from pathlib import Path

# Load EXPECTED_MSGIDS from the sibling conftest.py by path, rather than
# ``from conftest import ...``, so collection order doesn't matter when both
# extension test dirs are run together (each has its own conftest.py).
import importlib.util as _il

_spec = _il.spec_from_file_location(
    "_diataxis_diagram_conftest",
    Path(__file__).resolve().parent / "conftest.py",
)
assert _spec is not None and _spec.loader is not None
_mod = _il.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
EXPECTED_MSGIDS = _mod.EXPECTED_MSGIDS


_MSGID_RE = re.compile(r'^msgid\s+"(.*)"$', re.MULTILINE)


def _pot_msgids(outdir) -> set[str]:
    """Collect every ``msgid "..."`` string from the generated .pot files."""
    msgids: set[str] = set()
    for pot in outdir.rglob("*.pot"):
        msgids.update(_MSGID_RE.findall(pot.read_text(encoding="utf-8")))
    return msgids


def test_gettext_build_produces_pot(built_gettext):
    _app, out = built_gettext
    pot_files = list(out.rglob("*.pot"))
    assert pot_files, "expected at least one .pot file from the gettext build"


def test_diataxis_diagram_strings_extracted_into_pot(built_gettext):
    _app, out = built_gettext
    msgids = _pot_msgids(out)

    missing = [s for s in EXPECTED_MSGIDS if s not in msgids]
    assert not missing, (
        f"{len(missing)} of {len(EXPECTED_MSGIDS)} diataxis-diagram strings were "
        f"not extracted into the .pot; missing: {missing!r}"
    )


def test_diataxis_diagram_string_count(built_gettext):
    """Sanity check: exactly the 14 expected strings are extracted.

    Guards against accidental duplication or extra translatable nodes.
    """
    _app, out = built_gettext
    msgids = _pot_msgids(out)
    assert len(EXPECTED_MSGIDS) == 14
    assert all(s in msgids for s in EXPECTED_MSGIDS)