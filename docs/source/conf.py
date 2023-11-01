import os, sys
sys.path.insert(0, os.path.abspath("../.."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'krajjat'
copyright = '2023, Romain Pastureau'
author = 'Romain Pastureau'
release = '1.99.8'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

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

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_logo = 'img/krajjat-logo-black.png'
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
