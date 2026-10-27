"""Pytest fixtures for the cjkspace extension tests.

Builds tiny Sphinx projects in a temp directory — following the pattern of
the atomfeed/diataxis_diagram test suites — and inspects the rendered
HTML. A gettext build asserts ``.pot`` extraction stays verbatim, and a
compiled-catalog build reproduces the real translation workflow (msgstr
re-parsing) end to end.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest
from sphinx.application import Sphinx
from sphinx.locale import translators as _sphinx_translators


def _project_root() -> Path:
    """Path to the repository root (makes the in-tree extensions importable)."""
    return Path(__file__).resolve().parents[2]


def _ensure_extensions_importable() -> None:
    root = _project_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _conf_py(
    language: str = "en",
    *,
    extra: str = "",
    extensions: tuple[str, ...] = ("extensions.cjkspace",),
) -> str:
    """A minimal ``conf.py`` enabling the cjkspace extension.

    ``extra`` appends further configuration (``gettext_compact``,
    ``locale_dirs``, ...) for the gettext and translation builds.
    ``extensions`` lets a test build the very same project without the
    extension, to show the difference it makes.
    """
    return (
        f"extensions = {list(extensions)!r}\n"
        "project = \"Diátaxis\"\n"
        "author = \"Daniele Procida\"\n"
        f"language = {language!r}\n"
        "master_doc = \"index\"\n"
        "exclude_patterns = []\n"
        f"{extra}\n"
    )


def _build(
    tmp_path: Path,
    rst: str,
    *,
    language: str = "en",
    buildername: str = "html",
    extra_conf: str = "",
    extra_files: dict[str, bytes | str] | None = None,
    extensions: tuple[str, ...] = ("extensions.cjkspace",),
) -> tuple[Sphinx, Path]:
    """Build a one-page Sphinx project from a caller-supplied ``index.rst``.

    Returns ``(app, outdir)``; the rendered page is ``outdir / "index.html"``
    for the html builder, the catalogs under ``outdir`` for gettext.
    ``extra_files`` maps paths relative to ``srcdir`` to contents (used to
    install locale catalogs).
    """
    _ensure_extensions_importable()

    # Sphinx caches loaded catalogs in a process-wide dict keyed by text
    # domain, merging later catalogs as fallbacks. Without a reset, a build
    # would see msgstrs from an earlier test's project (same domain name).
    _sphinx_translators.clear()

    src = tmp_path / "src"
    out = tmp_path / "out"
    doctree = tmp_path / "doctrees"

    src.mkdir(parents=True)
    (src / "conf.py").write_text(
        _conf_py(language, extra=extra_conf, extensions=extensions),
        encoding="utf-8",
    )
    (src / "index.rst").write_text(rst, encoding="utf-8")
    for rel, content in (extra_files or {}).items():
        path = src / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            path.write_bytes(content)

    app = Sphinx(
        srcdir=str(src),
        confdir=str(src),
        outdir=str(out),
        doctreedir=str(doctree),
        buildername=buildername,
        freshenv=True,
    )
    app.build()
    return app, out


def _write_mo(catalog: dict[str, str]) -> bytes:
    """Compile a minimal GNU .mo file (no plurals, no context).

    Sphinx loads translations through Python's ``gettext``, which reads
    only compiled ``.mo`` files; this emits the standard layout — header,
    original-string table, translation-string table, then the strings.
    A metadata header entry (msgid ``""``) declares the UTF-8 charset,
    without which gettext would decode the catalog as ASCII.
    """
    catalog = {
        "": (
            "MIME-Version: 1.0\n"
            "Content-Type: text/plain; charset=UTF-8\n"
            "Content-Transfer-Encoding: 8bit\n"
        ),
        **catalog,
    }
    entries = sorted(catalog.items())
    ids = b""
    strs = b""
    offsets = []
    for msgid, msgstr in entries:
        msgid_b = msgid.encode()
        msgstr_b = msgstr.encode()
        offsets.append((len(ids), len(msgid_b), len(strs), len(msgstr_b)))
        ids += msgid_b + b"\x00"
        strs += msgstr_b + b"\x00"
    n = len(entries)
    keystart = 7 * 4 + 16 * n
    valuestart = keystart + len(ids)
    orig_table = b"".join(
        struct.pack("<ii", length, keystart + offset)
        for offset, length, _, _ in offsets
    )
    trans_table = b"".join(
        struct.pack("<ii", length, valuestart + offset)
        for _, _, offset, length in offsets
    )
    header = struct.pack(
        "<Iiiiiii",
        0x950412DE,           # magic
        0,                    # version
        n,                    # number of entries
        7 * 4,                # offset of the original-string table
        7 * 4 + 8 * n,        # offset of the translation-string table
        0,                    # hash table size (unused)
        0,                    # hash table offset (unused)
    )
    return header + orig_table + trans_table + ids + strs


@pytest.fixture
def build_html(tmp_path: Path):
    """Factory building one-page HTML projects; returns the outdir."""
    def _build_one(rst: str, **kwargs) -> Path:
        _app, out = _build(tmp_path, rst, buildername="html", **kwargs)
        return out
    return _build_one
