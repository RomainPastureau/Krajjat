import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'src')))
import krajjat

project = 'krajjat'
copyright = '2025, Romain Pastureau'
author = 'Romain Pastureau'
release = '1.99.20'

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx_tabs.tabs',
    'sphinx_copybutton',
    #'sphinx.ext.autosectionlabel',
    #'sphinx-autodoc-typehints',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_logo = 'img/krajjat_logo_black.png'
# html_static_path = ["_static"]

html_theme_options = {
    "logo_only": True,
    "style_nav_header_background": '#ffd242',
    "collapse_navigation": False,
    "navigation_depth": 4,
    "includehidden": False
}

html_static_path = ['_static']

html_css_files = [
    'css/custom.css',
]

napoleon_use_param = True