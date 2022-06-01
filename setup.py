"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import os
import pathlib
from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
version = {}
with open(os.path.join(here, "src", "cli", "version.py")) as fp:
  exec(fp.read(), version)

setup(
  version=version['__version__'],
)
