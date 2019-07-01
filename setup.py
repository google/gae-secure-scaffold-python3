#!/usr/bin/env python
import setuptools


with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Toaster Secure Scaffold Beta",
    version='0.6',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    author="Toaster Ltd.",
    author_email="developers@toaster.co",
    description="Secure Scaffold for Google App Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toasterco/gae-secure-scaffold-python",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
