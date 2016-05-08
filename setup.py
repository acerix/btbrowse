#!/usr/bin/env python3

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Single-sourced version number
# https://packaging.python.org/en/latest/single_source_version.html
version = {}
with open('./btbrowse/version.py') as fp:
    exec(fp.read(), version)

setup(
    name='btbrowse',

    version=version['__version__'],

    description='',
    keywords='torrent magnet btfs',
    long_description=long_description,
    url='https://github.com/acerix/btbrowse',
    author='acerix',
    author_email='acerix@psilly.com',
    license='GPL3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Communications :: File Sharing',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
	'Environment :: Console',
        'Operating System :: POSIX :: Linux'
    ],

    packages=['btbrowse'],

    package_data={
        'btbrowse': [
            'examples/*'
        ],
    },

    install_requires=[
        'pyxdg',
        'pytoml',
    ],

)

