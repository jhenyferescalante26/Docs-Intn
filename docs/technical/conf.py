project = "INTN Odoo — Documentación Técnica"
author = "Appex"
copyright = "2026, Appex"
language = "es"

extensions = [
    "myst_parser",
    "sphinx.ext.graphviz",
    "sphinxcontrib.mermaid",
    "sphinx.ext.autosectionlabel",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
myst_heading_anchors = 3

source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

graphviz_output_format = "svg"
autosectionlabel_prefix_document = True

exclude_patterns = [
    "_build",
    "README.md",
    "requirements-docs.txt",
    "Thumbs.db",
    ".DS_Store",
    "**/_templates/*",
]

html_theme = "furo"
html_title = "INTN Odoo — Documentación Técnica"
html_static_path = ["_static"]
suppress_warnings = ["autosectionlabel.*"]
