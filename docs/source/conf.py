#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# KATANA SDK for Python 3 documentation build configuration file, created by
# sphinx-quickstart on Fri Jan 27 15:37:32 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- General configuration ------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'KATANA SDK for Python 3'
copyright = '2016-2017 KUSANAGI S.L. All rights reserved'
author = 'Jerónimo Albi'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.0.0'
# The full version, including alpha/beta/rc tags.
release = '1.0.0-beta.4'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

add_module_names = False
html_show_sphinx = False

# Include both class docstring and __init__
autoclass_content = 'both'

autodoc_default_flags = [
    'members',
    'undoc-members',
    'show-inheritance',
    # 'inherited-members',
    # 'private-members',
    ]

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'KATANASDKforPython3doc'


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(
    master_doc,
    'katanasdkforpython3',
    'KATANA SDK for Python 3 Documentation',
    [author],
    1,
    )]


# -- Custom code -------------------------------

def remove_module_docstring(app, what, name, obj, options, lines):
    if what == 'module':
        del lines[:]


def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)
