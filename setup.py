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
    'invenio-app>=1.3.0,<2.0.0',
    'pytest-invenio>=1.4.1,<2.0.0'
]

invenio_db_version = '>=1.0.9,<2.0.0'
invenio_search_version = '>=1.4.0,<2.0.0'

extras_require = {
    'docs': [
        'Sphinx>=3,<3.4.2',
    ],
    # Elasticsearch version
    'elasticsearch6': [
        f'invenio-search[elasticsearch6]{invenio_search_version}',
    ],
    'elasticsearch7': [
        f'invenio-search[elasticsearch7]{invenio_search_version}',
    ],
    # Databases
    'mysql': [
        f'invenio-db[mysql,versioning]{invenio_db_version}',
    ],
    'postgresql': [
        f'invenio-db[postgresql,versioning]{invenio_db_version}',
    ],
    'sqlite': [
        f'invenio-db[versioning]{invenio_db_version}',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('elasticsearch6', 'elasticsearch7',
                'mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    "flask-resources>=0.7.0,<0.8.0",
    "invenio-accounts>=1.4.3",
    "invenio-assets>=1.2.2",
    "invenio-base>=1.2.3",
    "invenio-files-rest>=1.2.0",
    "invenio-i18n>=1.2.0",
    "invenio-indexer>=1.2.0",
    "invenio-jsonschemas>=1.1.2",
    "invenio-mail>=1.0.2",
    "invenio-pidstore>=1.2.2",
    "invenio-records-permissions>=0.11.0,<0.12.0",
    "invenio-records>=1.5.0a4",
    "invenio-records-resources>=0.15.1",
    "invenio-rdm-records>=0.29.4",
    "uritemplate>=3.0.1",
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
        'flask.commands': [
            'communities = invenio_communities.cli:communities',
        ],
        'invenio_base.apps': [
            'invenio_communities = invenio_communities:InvenioCommunities',
        ],
        'invenio_base.api_apps': [
            'invenio_communities = invenio_communities:InvenioCommunities',
        ],
        'invenio_base.blueprints': [
            'invenio_communities = invenio_communities.views:create_ui_blueprint',
            # 'invenio_communities_records = invenio_communities.communities.records.views:ui_blueprint',
            # 'invenio_communities_collections = invenio_communities.communities.records.collections.views:ui_blueprint',
        ],
        'invenio_base.api_blueprints': [
            'invenio_communities_api = invenio_communities.views:create_communities_api_blueprint',
        ],
        'invenio_db.models': [
            'invenio_communities = invenio_communities.communities.records.models',
            # 'invenio_communities_members = invenio_communities.members.models',
            # 'invenio_communities_records = invenio_communities.communities.records.models',
            # 'invenio_requests = invenio_communities.requests.models',
        ],
        'invenio_db.alembic': [
            'invenio_communities = invenio_communities:alembic',
        ],
        'invenio_search.mappings': [
            'communities = invenio_communities.communities.records.mappings',
        ],
        'invenio_jsonschemas.schemas': [
            'communities = invenio_communities.communities.records.jsonschemas',
        ],
        'invenio_assets.webpack': [
            'invenio_communities = invenio_communities.webpack:communities'
        ],
        'invenio_celery.tasks': [
            'invenio_communities = invenio_communities.fixtures.tasks',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 3 - Alpha",
     ],
)
