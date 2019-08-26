#!/usr/bin/env python
import setuptools


with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Toaster Secure Scaffold RC",
    version='0.8.2',
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    extras_require={
        'firestore': ['google-cloud-firestore==1.2.0'],
        'datastore': ['google-cloud-datastore==1.8.0'],
        'tasks': ['google-cloud-tasks==1.1.0'],
    },
    include_package_data=True,
    author="Toaster Ltd.",
    author_email="developers@toaster.co",
    description="Secure Scaffold for Google App Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toasterco/gae-secure-scaffold-python",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        secure_scaffold=secure_scaffold.commands:cli
    '''
)
