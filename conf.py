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

html_title = full_title = project = "Diátaxis"
copyright = "Daniele Procida"
author = "Daniele Procida"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx_design", "sphinx_reredirects"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "env",
    "LICENSE.rst",
    "README.rst",
    "stashed",
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": True,
    "light_css_variables": {
        "color-background-secondary": "#fff",
        "color-sidebar-background-border": "none",
    },
    "dark_css_variables": {
        "color-background-secondary": "#000",
    },
}
html_static_path = ["_static"]
html_logo = "images/diataxis-white-416.png"
html_css_files = [
    "diataxis.css",
]
html_sidebars = {
    "**": [
        "sidebar/scroll-start.html",
        "sidebar/brand.html",
        "sidebar/navigation.html",
        "sidebar/search.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

master_doc = "index"

html_favicon = "favicon.png"

spelling_lang = tokenizer_lang = "en_GB"

redirects = {
     "citation": "/colofon",
     "contact": "/colofon"
}
