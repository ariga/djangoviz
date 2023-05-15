#!/usr/bin/env python
# coding=utf-8

import io
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as fp:
    README = fp.read()


setup(
    name="djangoviz",
    use_scm_version={
        "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
    description="A visualization tool.",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        # See https://pypi.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="django erd visualization",
    author="Yoni Davidson",
    author_email="y@ariga.io",
    url="https://github.com/ariga/djangoviz",
    license="Apache License 2.0",
    packages=find_packages(exclude=["tests*"]),
    platforms=["any"],
    zip_safe=True,
    python_requires=">=3.6",
    install_requires=[
        "django>=2.2",
        "graphqlclient>=0.2.4",
    ],
    tests_require=[],
    extras_require={},
)
