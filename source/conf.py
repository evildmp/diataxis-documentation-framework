html_title = full_title = project = "Diátaxis"
copyright = "Daniele Procida"
author = "Daniele Procida"

# -- General configuration ---------------------------------------------------

extensions = ["sphinx_design", "sphinx_reredirects"]

templates_path = ["../_templates"]

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
html_css_files = ["diataxis.css"]
html_js_files = [
    "language-switcher.js",
]
language_switcher = [
    ["en", "English"],
    ["fr", "Français"],
    ["it", "Italiano"],
    ["pt_BR", "Português"],
    # ["zh_CN", "简体中文"],
    # ["de", "Deutsche"],
    ["pl", "Polski"],
    ["ja", "日本語"],
]
html_context = {
    "language_switcher": language_switcher,
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

# Translation settings

language = "en"
locale_dirs = ["../translation"]
gettext_compact = False
gettext_uuid = False
gettext_location = True
