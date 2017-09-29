extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.viewcode']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = 'GitHub Ticket Gnome'
copyright = '2017, Team Bugflow'
author = 'Team Bugflow'
version = '0.0.0'
release = '0.0.0'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
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
htmlhelp_basename = 'GitHubTicketGnomedoc'
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}
latex_documents = [
    (master_doc, 'GitHubTicketGnome.tex', 'GitHub Ticket Gnome Documentation',
     'Team Bugflow', 'manual'),
]
man_pages = [
    (master_doc, 'githubticketgnome', 'GitHub Ticket Gnome Documentation',
     [author], 1)
]
texinfo_documents = [
    (master_doc, 'GitHubTicketGnome', 'GitHub Ticket Gnome Documentation',
     author, 'GitHubTicketGnome', 'One line description of project.',
     'Miscellaneous'),
]
