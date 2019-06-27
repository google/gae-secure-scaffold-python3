#!/usr/bin/env python
import setuptools


with open("requirements.txt") as f:
    install_requires = f.read().splitlines()


setuptools.setup(
    name="Secure Scaffold",
    version='0.5',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    author="Toaster Ltd.",
    author_email="Toaster Ltd.",
    description="Secure Scaffold for Google App Engine",
)
