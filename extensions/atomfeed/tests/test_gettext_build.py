"""Test that non-HTML builders don't trip atomfeed's build-finished hook.

``make gettext`` runs Sphinx's ``MessageCatalogBuilder``, which has no
``docwriter`` attribute. atomfeed's ``on_build_finished`` used to call
``build_feed`` unconditionally, reaching into ``builder.docwriter`` and
raising ``AttributeError: 'MessageCatalogBuilder' object has no attribute
'docwriter'``. The hook now skips feed generation for non-HTML builders.
"""

from __future__ import annotations


def test_gettext_build_does_not_raise(built_gettext):
    # Should not raise ExtensionError about a missing 'docwriter'.
    _app, out = built_gettext

    # The gettext builder writes .pot files into <outdir>.
    pot_files = list(out.rglob("*.pot"))
    assert pot_files, "expected at least one .pot file from the gettext build"

    # And it must not have produced an atom.xml: the feed is HTML-only.
    assert not (out / "atom.xml").exists(), (
        "atomfeed wrote atom.xml during a gettext build; the feed should "
        "only be generated for HTML builders"
    )


def test_message_catalog_builder_has_no_docwriter(built_gettext):
    """Regression premise: the gettext builder genuinely lacks a docwriter.

    If this ever changes, the guard in ``on_build_finished`` becomes
    unnecessary and this test should be revisited.
    """
    app, _out = built_gettext
    assert not hasattr(app.builder, "docwriter"), (
        "MessageCatalogBuilder now has a docwriter; the regression premise "
        "no longer holds and this test needs revisiting"
    )
    # And the builder's format is not "html", which is what the guard
    # checks.
    assert getattr(app.builder, "format", None) != "html"


def test_build_feed_raises_without_docwriter(built_gettext):
    """Calling build_feed on a builder without a docwriter must raise.

    This pins the failure mode the ``on_build_finished`` guard prevents:
    without the guard, the same call happens during ``build-finished``
    and crashes the whole build.
    """
    import extensions.atomfeed as atomfeed

    app, _out = built_gettext
    try:
        atomfeed.build_feed(app)
    except AttributeError as exc:
        assert "docwriter" in str(exc)
    else:
        raise AssertionError(
            "build_feed did not raise AttributeError on a builder without "
            "docwriter; the regression premise no longer holds"
        )
