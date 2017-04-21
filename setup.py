#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'markupsafe',
]

test_requirements = [
    'pytest>=2.10',
    'pytest-cov',
    'tox',
]

setup(
    name='diffhtml',
    version='0.1.0',
    description="Tools for generating HTML diff output.",
    long_description=readme + '\n\n' + history,
    author="Tzu-ping Chung",
    author_email='uranusjr@gmail.com',
    url='https://github.com/uranusjr/diffhtml',
    packages=[
        'diffhtml',
    ],
    package_dir={
        'diffhtml': 'diffhtml',
    },
    include_package_data=True,
    install_requires=requirements,
    license="ISC license",
    zip_safe=False,
    keywords='diffhtml',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
