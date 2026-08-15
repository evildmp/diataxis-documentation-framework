import os
import sys

sys.path.insert(0, os.path.abspath("../extensions"))

html_title = full_title = project = "Diátaxis"
copyright = "Daniele Procida"
author = "Daniele Procida"

# -- General configuration ---------------------------------------------------

extensions = ["sphinx_design", "sphinx_reredirects", "atomfeed", "diataxis_diagram"]

templates_path = ["../_templates"]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "env",
    "LICENSE.rst",
    "README.rst",
    "stashed",
    "snippets",
]

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_theme_options = {
    "sidebar_hide_name": True,
    "top_of_page_buttons": [],
    "light_css_variables": {
        "color-background-secondary": "#fff",
        "color-sidebar-background-border": "none",
    },
    "dark_css_variables": {
        "color-background-secondary": "#000",
    },
}
html_static_path = ["../_static"]
html_logo = "images/diataxis-white-416.png"
html_css_files = ["diataxis.css", "skia-font.css"]
html_js_files = ["language-switcher.js"]
html_context = {
    "language_switcher": [
        ["en", "English"],
        ["pl", "Polski"],
        # ["fr", "Français"],
        # ["it", "Italiano"],
        # ["pt_BR", "Português"],
        # ["zh_CN", "简体中文"],
        # ["de", "Deutsche"],
        # ["ja", "日本語"],
        # ["ko", "한국어"],
    ],
    "default_language": "en",
}
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

html_permalinks_icon = "¶"

html_show_sphinx = False

master_doc = "index"

html_favicon = "../favicon.png"

spelling_lang = tokenizer_lang = "en_GB"
spelling_word_list_filename = "../spelling_wordlist.txt"
spelling_filters=["sphinxcontrib.spelling.filters.ContractionFilter"]



redirects = {
     "citation": "/colophon",
     "contact": "/colophon",
     "colofon": "/colophon",
}

# -- Translation settings ---------------------------------------------------

language = "en"
locale_dirs = ["../translation"]
translation_exclude_patterns = ["translation.rst"]
gettext_compact = False
gettext_uuid = False
gettext_location = True

diataxis_diagram = {
    "default": {
      "font-sizes": {"type": 105, "purpose": 50, "axis": 55},
      "offsets": {
          "axis-x": 154,
          "type-purpose-x": 154,
          "type-x-correction": 0,
          "axis-y": 110,
          "purpose-y": 120,
          "type-y": 260
      },
      "y-axis-rotation": "rotated",
      "guides": False
    },
    "en": {},
    "pl": {"font-sizes": {"type": 57, "purpose": 44, "axis": 44}},
    # "it": {"font-sizes": {"type": 100, "purpose": 44, "axis": 44}},
    # "fr": {"font-sizes": {"type": 100, "purpose": 44, "axis": 44}},
    # "zh_CN": {"font-sizes": {"type": 104, "purpose": 44, "axis": 80}, "layout": {"y-axis-rotation": "stacked"}},
    # "pt_BR": {"font-sizes": {"type": 104, "purpose": 44, "axis": 80}, "layout": {"y-axis-rotation": "stacked"}},
    # "ko": {"font-sizes": {"type": 104, "purpose": 44, "axis": 80}, "layout": {"y-axis-rotation": "stacked"}},
    # "ja": {"font-sizes": {"type": 104, "purpose": 44, "axis": 80}, "layout": {"y-axis-rotation": "stacked"}},

}

# -- Atom feed configuration ---------------------------------------------------

atom_feed_base_url = "https://diataxis.fr"
atom_feed_source = "news"
atom_feed_author = author

# -- exclude selected files from translation -------------------------------

def setup(app):
    app.add_config_value("translation_exclude_patterns", [], "env")

    def drop_excluded_pots(app, exception):
        if app.builder.name != "gettext" or exception is not None:
            return
        for name in app.config.translation_exclude_patterns:
            stem = name.removesuffix(".rst")
            (app.builder.outdir / f"{stem}.pot").unlink(missing_ok=True)

    app.connect("build-finished", drop_excluded_pots)
