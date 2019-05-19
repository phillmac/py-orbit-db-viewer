#!/usr/bin/env python

from orbitdbviewer import __version__
from setuptools import setup, find_packages

setup(
    name='orbitdbviewer',
    version=__version__,
    description='A Python HTTP Orbitdb API Client',
    author='Phillip Mackintosh',
    url='https://github.com/phillmac/py-orbit-db-viewer',
    packages=find_packages(),
    package_data={'orbitdbviewer': ['templates/*']},
    install_requires=[
        'orbitdbapi ~= 0.2.1.dev0',
        'ipfsapi ~= 0.4.3',
        'flask ~= 1.0.2',
        'flask_wtf ~= 0.14.2',
        'bootstrap-flask ~= 1.0.4'
        ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
