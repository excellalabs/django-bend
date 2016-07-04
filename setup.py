#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "django_bend",
    version = "1.0.0",
    license = "public domain",
    classifiers=[
    'Programming Language :: Python :: 2'
    'Programming Language :: Python :: 2.7'
    'Programming Language :: Python :: 3'
    'Programming Language :: Python :: 3.4'
    'Programming Language :: Python :: 3.5'
    ]
    packages = find_packages(),
    install_requires=[
        'simplejson>=3.8.0',
    ]
)
