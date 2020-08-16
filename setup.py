# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module that adds support for communities."""

from __future__ import absolute_import, print_function

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'pytest-invenio>=1.3.2,<2.0.0',
    'invenio-app>=1.3.0,<2.0.0'
]

invenio_db_version = '>=1.0.4,<2.0.0'
invenio_search_version = '1.2.2'

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    # Elasticsearch versions
    'elasticsearch6': [
        'invenio-search[elasticsearch6]>={}'.format(invenio_search_version),
    ],
    'elasticsearch7': [
        'invenio-search[elasticsearch7]>={}'.format(invenio_search_version),
    ],
    # Databases
    'mysql': [
        'invenio-db[mysql,versioning]{}'.format(invenio_db_version),
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]{}'.format(invenio_db_version),
    ],
    'sqlite': [
        'invenio-db[versioning]{}'.format(invenio_db_version),
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('elasticsearch6', 'elasticsearch7',
                'mysql',' postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.7',
]

install_requires = [
    'invenio-i18n>=1.1.0',
    'invenio-base>=1.2.2',
    'invenio-accounts>=1.1.0',
    'invenio-assets>=1.2.2',
    'invenio-indexer>=1.1.1',
    'invenio-jsonschemas>=1.1.0,<2.0.0',
    'invenio-pidstore>=1.1.0',
    'invenio-records-permissions>=0.9.0',
    'invenio-records-rest>=1.6.0',
    'invenio-records>=1.2.0',
    'invenio-rest>=1.1.0',
    'invenio-mail>=1.0.2'
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_communities', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-communities',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio communities',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-communities',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_communities = invenio_communities:InvenioCommunities',
        ],
        'invenio_base.api_apps': [
            'invenio_communities = invenio_communities:InvenioCommunities',
        ],
        'invenio_base.blueprints': [
            'invenio_communities = invenio_communities.views:ui_blueprint',
            'invenio_communities_members = invenio_communities.members.views:ui_blueprint',
            'invenio_communities_records = invenio_communities.records.views:ui_blueprint',
        ],
        'invenio_base.api_blueprints': [
            'invenio_communities_members = invenio_communities.members.views:api_blueprint',
            'invenio_communities_records = invenio_communities.records.views:api_blueprint',
        ],
        'invenio_db.models': [
            'invenio_communities = invenio_communities.models',
            'invenio_communities_members = invenio_communities.members.models',
            'invenio_communities_records = invenio_communities.records.models',
            'invenio_requests = invenio_communities.requests.models',
        ],
        'invenio_search.mappings': [
            'communities = invenio_communities.mappings',
        ],
        'invenio_pidstore.minters': [
            'comid = invenio_communities.minters:comid_minter',
        ],
        'invenio_pidstore.fetchers': [
            'comid = invenio_communities.fetchers:comid_fetcher',
        ],
        'invenio_jsonschemas.schemas': [
            'communities = invenio_communities.jsonschemas',
        ],
        'invenio_assets.webpack': [
            'invenio_communities = invenio_communities.webpack:communities'
        ],
        'invenio_celery.tasks': [
            # TODO: Add when necessary
            # 'invenio_communities = invenio_communities.tasks',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 3 - Alpha',
    ],
)
