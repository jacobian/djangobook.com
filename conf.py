# Basic project info
project = u'The Django Book'
copyright = u'Adrian Holovaty, Jacob Kaplan-Moss, et al.'
version = '2.0'
release = '2.0'

# Build options
templates_path = ['_templates']
exclude_patterns = ['_build', 'README.rst']
source_suffix = '.rst'
master_doc = 'index'

# HTML options
html_theme = 'djangobook'
html_theme_path = ['themes']
html_static_path = ['_static']
pygments_style = 'sphinx'
html_use_index = False          # FIXME once proper index directives are added.
html_show_sourcelink = False
html_show_sphinx = False
html_title = "The Django Book"
html_add_permalinks = False     # FIXME once styles are fixed to get the hover back.

# LATEX builder
latex_documents = [
  ('index', 'TheDjangoBook.tex', u'The Django Book',
   u'Adrian Holovaty, Jacob Kaplan-Moss, et al.', 'manual'),
]

# texinfo builder
texinfo_documents = [
    ('index', 'TheDjangoBook.tex', u'The Django Book',
     u'Adrian Holovaty, Jacob Kaplan-Moss, et al.', 'manual'),
    ]

# ePub builder
epub_title = u'The Django Book'
epub_author = u'Adrian Holovaty, Jacob Kaplan-Moss, et al.'
epub_publisher = u'Adrian Holovaty, Jacob Kaplan-Moss, et al.'
epub_copyright = u'Adrian Holovaty, Jacob Kaplan-Moss, et al.'
