#!/usr/bin/env python
import setuptools


with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Secure Scaffold",
    version="0.1",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=install_requires,
    include_package_data=True,
    author="Google",
    author_email="developers@toaster.co",
    description="Secure Scaffold for Google App Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/davidwtbuxton/gae-secure-scaffold-python",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
