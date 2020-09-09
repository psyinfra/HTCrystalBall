#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join as opj, dirname
import re

version_file = 'htcrystalball/_version.py'
readme = opj(dirname(__file__), 'README.md')
mo = re.search(
    r"^__version__ = ['\"]([^'\"]*)['\"]",
    open(version_file, "rt").read(),
    re.M
)

if mo:
    version = mo.group(1)
else:
    raise RuntimeError('Unable to find version string in %s.' % version_file)

try:
    import pypandoc
    long_description = pypandoc.convert(readme, 'rst')

except (ImportError, OSError) as exc:
    print('WARNING: pypandoc failed to import or threw an error while '
          'converting README.md to RST: %s .md version will be used as is'
          % exc)
    long_description = open(readme).read()

setup(
    name='HTCrystalBall',
    version=version,
    author='Jona Fischer and many others',
    author_email='j.fischer@fz-juelich.de',
    description='HTCondor preview script',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/psyinfra/HTCrystalBall',
    license='ISC',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6.0',
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'htcb=htcrystalball.main:main',
            'htcrystalball=htcrystalball.main:main'
        ],
    },
    install_requires=[
        'rich>=6.1.1',
        'htcondor>=8.9.8',
    ],
    tests_require=[
        'pytest>=6.0.1',
    ]
)
