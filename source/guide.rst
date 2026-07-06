==============================================================
Daniele's guide to translation: Sphinx, RTD, Github, Transifex
==============================================================

This is a pretty standard workflow for Sphinx documentation:

You maintain your documentation source in Git, on GitHub. It's published on Read the Docs. Translations are managed on Transifex.

All three platforms - GitHub, RTD and Transifex - play nicely together so that changes to the project's content are automatically sent for translation to Transifex, and get themselves published, all with minimal work for you the maintainer.


Basic translation workflow
==========================

The very basic translation workflow is:

* generate a ``.pot`` file ("Portable Object Template" – essentially, translation source files)  for each of the pages of your documentation
* generate/update corresponding ``.po`` files for each target language
* edit the ``.po`` files to add/update the translations
* build the translated documentation from the ``.po`` files

When using Transifex, instead of editing ``.po`` files locally, the source strings in the ``.pot`` files are sent to Transifex, translated there, and then the translated strings pulled back down into ``.po`` files.


Configuration
==============
You need to have your project up and running, and published on RTD.

Edit ``conf.py``::

    # Translation settings

    language = "en"             # the source documentation language
    locale_paths = ["translation/targets"]  # where the translations will live
    gettext_compact = False      # don't mash all the files into one
    gettext_uuid = True          # use stable identifiers for messages

We need a ``transifex.yaml`` file in the repository, so Transifex knows how to behave::

    git:
      filters:
        - filter_type: dynamic
          file_format: PO
          source_language: en
          source_files_expression: translation/source/<file>.pot
          translation_files_expression: translation/targets/<lang>/LC_MESSAGES/<file>.po


Executing the workflow
======================

Generate the ``.pot`` files
Run: ``make gettext``. This will create a ``gettext`` directory inside your build directory (usually, ``_build``) containing a ``.pot`` file for each page.

``_build`` is excluded from commits, but the ``.pot`` files need to be committed, so use ``make copy-pot-files`` to copy them to ``.pot`` files in ``translation/source``.

Then the changes can be committed and pushed.

The next thing is to get the ``.pot`` files into Transifex. Transifex should do that itself, watching GitHub for changes.
