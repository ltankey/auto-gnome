import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

from paver.easy import *
import paver.doctools
from paver.setuputils import setup, Bunch

setup(
    name = "auto-gnome",
    packages = [".",]
)

options(
    sphinx=Bunch(
        builddir="_build",
        docroot="."
    )
)
