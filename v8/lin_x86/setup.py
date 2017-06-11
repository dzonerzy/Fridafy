#!/usr/bin/env python

import os

from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="PyV8",
    version="0.1",
    author="Daniele Linguaglossa",
    description="PyV8 binary for Linux x86",
    license="",
    packages=find_packages(),
    zip_safe=False,
    package_data={
        'pyv8': ['*.so'],     # include .so files when installed with pip/git
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ]
)
