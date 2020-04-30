# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS bundles for communities.

You include one of the bundles in a page like the example below (using
``comunities`` bundle as an example):

.. code-block:: html

    {{ webpack['communities.js']}}

"""

from __future__ import absolute_import, print_function

from flask_webpackext import WebpackBundle

communities = WebpackBundle(
    __name__,
    'assets',
    entry={
        'communities-theme': './scss/invenio_communities/theme.scss',
        'communities-new': './js/invenio_communities/new.js',
        'communities-members': './js/invenio_communities/members.js',
        'communities-request': './js/invenio_communities/request.js',
        'communities-curation': './js/invenio_communities/curation.js',
        'communities-records': './js/invenio_communities/records.js',
        'communities-search': './js/invenio_communities/communities_search.js',
        'communities-records-search': './js/invenio_communities/communities_records_search.js',

    },
    dependencies={
        'semantic-ui-css': '^2.4.1',
        'semantic-ui-react': '^0.88.2',
        '@ckeditor/ckeditor5-build-classic': '^16.0.0',
        '@ckeditor/ckeditor5-react': '^2.1.0',
        'axios': '^0.19.0',
        'formik': '^2.0.6',
        'lodash': '^4.17.15',
        'luxon': '^1.21.1',
        'path': '^0.12.7',
        'prop-types': '^15.7.2',
        'qs': '^6.9.1',
        'react': '^16.12.0',
        'react-dom': '^16.11.0',
        'react-redux': '^7.1.3',
        'react-searchkit': '^0.15.0',
        'redux': '^4.0.5',
        'redux-thunk': '^2.3.0',
        'yup': '^0.27.0',
    }
)
