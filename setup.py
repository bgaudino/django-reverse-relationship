#!/usr/bin/env python

from setuptools import setup

__doc__ = "A model form and admin class that includes reverse related fields"

install_requires = [
    "Django>=3.2",
]

setup(
    name="django-reverse-relationship-form",
    version="0.1.0.dev0",
    author="Brian Gaudino",
    author_email="bgaudino@gmail.com",
    description=__doc__,
    packages=["reverse_relationship_form"],
    install_requires=install_requires,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2"
        "Framework :: Django :: 4.0"
        "Framework :: Django :: 4.1"
        "Framework :: Django :: 4.2"
        "Framework :: Django :: 5.0"
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
