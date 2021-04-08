# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 UCT Prague.
#
# oarepo-validate is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""OArepo Validate library for record metadata validation"""

import os

from setuptools import find_packages, setup

readme = open('README.md').read()
history = open('CHANGES.md').read()
OAREPO_VERSION = os.environ.get('OAREPO_VERSION', '3.3.0')

install_requires = [
    'wrapt>=1.11.2',
]

tests_require = [
    f'oarepo[tests]~={OAREPO_VERSION}'
]

extras_require = {
    'tests': tests_require,
    'dev': [
        *tests_require,
        'invenio-app',
        'redis',
        'markdown-toc'
    ]
}

setup_requires = [
    'pytest-runner>=2.7',
]

packages = find_packages(exclude=["tests"])

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('oarepo_validate', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='oarepo-validate',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    keywords='metadata validation oarepo records',
    license='MIT',
    author='UCT Prague',
    author_email='miroslav.simek@vscht.cz',
    url='https://github.com/oarepo/oarepo-validate',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    entry_points={
        'flask.commands': [
            'oarepo:validate = oarepo_validate.cli:validate',
        ],
        'invenio_base.apps': [
            'oarepo_validate = oarepo_validate.ext:OARepoValidate',
        ],
        'invenio_base.api_apps': [
            'oarepo_validate = oarepo_validate.ext:OARepoValidate',
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Development Status :: 4 - Beta',
    ],
)
