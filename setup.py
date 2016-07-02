#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "django_bend",
    version = "1.0.0",
    license = "public domain",
    packages = find_packages(),
    install_requires=[
        'simplejson>=3.8.0',
    ]
)
