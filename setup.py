"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

import os
import pathlib
from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()
# https://packaging.python.org/en/latest/guides/single-sourcing-package-version/
with open(os.path.join(here, "src", "cli", "VERSION.txt")) as version_file:
  version = version_file.read().strip()

setup(
  version=version,
  package_data={
    "": ["VERSION.txt"]
  },
)
