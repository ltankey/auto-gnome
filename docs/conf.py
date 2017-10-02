import os
import sys
sys.path.insert(0, os.path.abspath('../src'))
sys.path.insert(0, os.path.abspath('../src/tests'))

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.viewcode',
              'sphinx.ext.graphviz']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'Bugflow Auto Gnome'
copyright = '2017, Team Bugflow'
author = 'Team Bugflow'
version = '0.0.0'
release = '0.0.0'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.venv']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'alabaster'
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'donate.html',
    ]
}
htmlhelp_basename = 'BugflowAutoGnomedoc'
latex_elements = {
    'papersize': 'a4paper',
}
latex_documents = [
    (master_doc, 'BugflowAutoGnome.tex', 'Bugflow Auto Gnome Documentation',
     'Team Bugflow', 'manual'),
]
texinfo_documents = [
    (master_doc, 'BugflowAutoGnome', 'Bugflow Auto Gnome Documentation',
     author, 'BugflowAutoGnome', 'One line description of project.',
     'Miscellaneous'),
]
