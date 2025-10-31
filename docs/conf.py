import os
import sys

# Add project root to sys.path for autodoc
sys.path.insert(0, os.path.abspath('..'))

project = 'Project Management System'
author = 'Project Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
html_static_path = ['_static']


