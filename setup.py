"""
MIT License

Copyright (c) 2017 Daniele Linguaglossa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from setuptools import setup
import subprocess
from v8 import *
import argparse
import sys

def install_v8(path):
    subprocess.Popen(["python", path, "install"]).wait()

parser = argparse.ArgumentParser("Fridafy Installer")
group = parser.add_mutually_exclusive_group()
group.add_argument("--osx", action="store_true", default=False, dest="osx", help="Install Fridafy for OSX")
group.add_argument("--linux-x86", action="store_true", default=False, dest="nix32", help="Install Fridafy for Linux 32bit")
group.add_argument("--linux-x86-64", action="store_true", default=False, dest="nix64", help="Install Fridafy for Linux 64bit")
group.add_argument("--win-x86", action="store_true", default=False, dest="win32", help="Install Fridafy for Windows 32bit")
group.add_argument("--win-x86-64", action="store_true", default=False, dest="win64", help="Install Fridafy for Windows 64bit")
args = parser.parse_args()
print args
if not (args.osx  | args.nix32 | args.nix64 | args.win32 | args.win64):
    print("Error: You must select at least an architecture!")
else:
    if args.osx:
        install_v8(PYV8_OSX)
    elif args.nix32:
        install_v8(PYV8_LINUX_32)
    elif args.nix64:
        install_v8(PYV8_LINUX_64)
    elif args.win32:
        install_v8(PYV8_WINDOWS_32)
    elif args.win64:
        install_v8(PYV8_WINDOWS_64)

    sys.argv = [sys.argv[0]]
    sys.argv.append("install")

    setup(
        name="Fridafy",
        version="0.1",
        author="Daniele Lingualossa",
        author_email="danielelinguaglossa@gmail.com",
        description="Simplified JS Engine for frida instrumentation tool",
        license="MIT",
        keywords="",
        url="https://github.com/dzonerzy/Fridafy",
        packages=["fridafy"],
        entry_points={
            'console_scripts': [
                    'fridafy=fridafy.fridafy:main'
            ]
        },
        classifiers=[
            "Topic :: Mobile"
        ],
        install_requires=[
            'frida',
        ],
    )
