import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fuelog._version import __version__

project = "fuelog-python"
author = "Fuelog"
release = __version__
version = __version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "member-order": "bysource",
}
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "furo"
html_title = f"fuelog-python {release}"
html_theme_options = {
    "source_repository": "https://github.com/Irishsmurf/fuelog-python",
    "source_branch": "main",
    "source_directory": "docs/",
}

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
