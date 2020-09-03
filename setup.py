#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

#
# Grab some info from supporting files
#
with open('README.md', 'r') as fh:
    long_description = fh.read()

__version__ = '.'.join(map(str, (0, 1, 0)))

#
# Provide a little info about who we are
#
setuptools.setup(
    name='HTCrystalBall',
    version=__version__,
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
    python_requires="!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*",
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        'rich',
        'htcondor'
    ],
    tests_require=[
        'pytest',
    ],
    data_files=[
            ('share/man/man1', ['man/man1/htcrystalball.1', 'man/man1/fetch_condor_slots.1'])
      ],
)
