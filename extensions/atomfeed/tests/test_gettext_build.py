"""Test that non-HTML builders don't produce atomfeed artifacts.

``make gettext`` runs Sphinx's ``MessageCatalogBuilder``. The feed is an
HTML artifact, so atomfeed's ``on_build_finished`` skips feed generation
for builders whose ``format`` is not ``html``.

Since Sphinx 9 removed ``builder.docwriter``, ``build_feed`` no longer
depends on builder-specific attributes (fragments are rendered via
``new_document`` + ``builder.docsettings``), so the format guard — not a
missing attribute — is what keeps atom.xml out of non-HTML output.
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


def test_message_catalog_builder_lacks_html_internals(built_gettext):
    """Regression premise: the gettext builder lacks the internals
    ``build_feed`` renders fragments with.

    Sphinx 9 removed ``builder.docwriter`` everywhere; fragment rendering
    now uses ``builder.docsettings``, which only builders that run
    ``prepare_writing`` (i.e. HTML builders) have. If a non-HTML builder
    ever grows these attributes, the format guard in
    ``on_build_finished`` becomes unnecessary and this test should be
    revisited.
    """
    app, _out = built_gettext
    assert not hasattr(app.builder, "docwriter")
    assert not hasattr(app.builder, "docsettings")
    # And the builder's format is not "html", which is what the guard
    # checks.
    assert getattr(app.builder, "format", None) != "html"


def test_build_feed_raises_without_docsettings(built_gettext):
    """Calling build_feed on a builder without ``docsettings`` must raise.

    This pins the failure mode the ``on_build_finished`` format guard
    prevents: without the guard, the same call happens during
    ``build-finished`` and crashes the whole build.
    """
    import extensions.atomfeed as atomfeed

    app, _out = built_gettext
    try:
        atomfeed.build_feed(app)
    except AttributeError as exc:
        assert "docsettings" in str(exc)
    else:
        raise AssertionError(
            "build_feed did not raise AttributeError on a builder without "
            "docsettings; the regression premise no longer holds"
        )
