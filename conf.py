# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Documentation system'
copyright = '2020, Daniele Procida'
author = 'Daniele Procida'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
try:
    import divio_docs_theme
except ModuleNotFoundError:
    html_theme = 'alabaster'
else:
    html_theme = 'divio_docs_theme'
    html_theme_path = [divio_docs_theme.get_html_theme_path()]
    html_theme_options = {
        'show_cloud_banner': True,
        'cloud_banner_markup': """
            <div class="divio-cloud">
                <span class="divio-cloud-caption">Cloud management by Divio</span>
                <p>If you like our attitude to documentation, you'll love the way we do cloud management.</p>
                <a class="btn-neutral divio-cloud-btn" target="_blank" href="https://goo.gl/nHv16j">Talk to us</a>
            </div>
        """,
    }


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

master_doc = 'index'


