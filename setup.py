#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = None
for line in open('./solve360/__init__.py'):
    m = re.search('__version__\s*=\s*(.*)', line)
    if m:
        version = m.group(1).strip()[1:-1]
        break
assert version


def publish():
    """Publish to PyPi"""
    os.system("python setup.py sdist upload")


if sys.argv[-1] == "publish":
    publish()
    sys.exit()

long_description = ''

try:
    os.system('pandoc --from=markdown --to=rst --output=README.rst README.md')
    long_description = open('README.rst').read()
except IOError:
    long_description = open('README.md').read()

setup(
    name='solve360',
    version=version,
    description='Solve360 API Python wrapper',
    long_description=long_description,
    author='Daniel Nibon',
    author_email='daniel@nibon.se',
    url='https://github.com/nibon/solve360',
    install_requires=['requests>=1.0.0'],
    tests_require=['pytest>=2.0.0'],
    packages=['solve360'],
    package_data={'': ['*.rst', '*.md']},
    license='Apache 2.0',
    keywords='norada solve solve360 api wrapper',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
)
