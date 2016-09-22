# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module that adds support for communities."""

from __future__ import absolute_import, print_function

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'Flask-CLI>=0.2.1',
    'invenio-mail>=1.0.0a3',
    'invenio-oaiserver>=1.0.0a2',
    'isort>=4.2.2',
    'mock>=1.3.0',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
]

extras_require = {
    'access': [
        'invenio-access>=1.0.0a1',
    ],
    'admin': [
        'Flask-Admin>=1.3.0',
    ],
    'docs': [
        'Sphinx>=1.4.2',
    ],
    'mail': [
        'Flask-Mail>=0.9.1',
    ],
    'oai': [
        'invenio-oaiserver>=1.0.0a2',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for reqs in extras_require.values():
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.7',
]

install_requires = [
    'Flask-BabelEx>=0.9.3',
    'invenio-accounts>=1.0.0a13',
    'invenio-access>=1.0.0a5',
    'invenio-assets>=1.0.0b2',
    'invenio-db>=1.0.0b1',
    'invenio-files-rest>=1.0.0.a1',
    'invenio-indexer>=1.0.0a6',
    'invenio-pidstore>=1.0.0a9',
    'invenio-records>=1.0.0a17',
    'invenio-rest[cors]>=1.0.0a9',
    'invenio-search>=1.0.0a7',
    'marshmallow>=2.5.0',
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
    license='GPLv2',
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
        'invenio_base.blueprints': [
            'invenio_communities = invenio_communities.views.ui:blueprint',
        ],
        'invenio_base.api_apps': [
            'invenio_communities = invenio_communities:InvenioCommunities',
        ],
        'invenio_base.api_blueprints': [
            'invenio_communities = invenio_communities.views.api:blueprint',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_communities',
        ],
        'invenio_access.actions': [
            'communities_create'
            ' = invenio_communities.permissions:communities_create',
            'communities_read'
            ' = invenio_communities.permissions:communities_read',
            'communities_edit'
            ' = invenio_communities.permissions:communities_edit',
            'communities_delete'
            ' = invenio_communities.permissions:communities_delete',
            'communities_curate'
            ' = invenio_communities.permissions:communities_curate',
            'communities_team'
            ' = invenio_communities.permissions:communities_team'
        ],
        'invenio_admin.views': [
            'invenio_communities_communities = '
            'invenio_communities.admin:community_adminview',
            'invenio_communities_requests = '
            'invenio_communities.admin:request_adminview',
            'invenio_communities_featured = '
            'invenio_communities.admin:featured_adminview',
        ],
        'invenio_assets.bundles': [
            'invenio_communities_js = invenio_communities.bundles:js',
            'invenio_communities_css = invenio_communities.bundles:css',
            'invenio_communities_select_js = invenio_communities.bundles:jsselect',
            'invenio_communities_select_css = invenio_communities.bundles:csselect'
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
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
