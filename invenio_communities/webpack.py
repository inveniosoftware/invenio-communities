# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS bundles for communities.

You include one of the bundles in a page like the example below (using
``comunities`` bundle as an example):

.. code-block:: html

    {{ webpack['communities.js']}}

"""

from invenio_assets.webpack import WebpackThemeBundle

communities = WebpackThemeBundle(
    __name__,
    'assets',
    default='semantic-ui',
    themes={
        'semantic-ui': dict(
            entry={
                'invenio-communities-theme':
                    './less/invenio_communities/theme.less',
                'invenio-communities-new':
                    './js/invenio_communities/new.js',
                'invenio-communities-privileges':
                    './js/invenio_communities/settings/privileges.js',
                'invenio-communities-profile':
                    './js/invenio_communities/settings/profile/index.js',
                'invenio-communities-frontpage':
                    './js/invenio_communities/frontpage.js',
                # 'invenio-communities-members':
                #     './js/invenio_communities/members.js',
                # 'invenio-communities-request':
                #     './js/invenio_communities/request.js',
                # 'invenio-communities-records':
                #     './js/invenio_communities/records.js',
                'invenio-communities-search':
                    './js/invenio_communities/search.js',
                # 'invenio-communities-records-search':
                #     './js/invenio_communities/records_search.js',
                # 'invenio-communities-records-curate':
                #     './js/invenio_communities/curate.js',
                # 'invenio-communities-collections-settings':
                #     './js/invenio_communities/collections/settings.js',
            },
            dependencies={
                '@ckeditor/ckeditor5-build-classic': '^16.0.0',
                '@ckeditor/ckeditor5-react': '^2.1.0',
                '@semantic-ui-react/css-patch': '^1.0.0',
                'axios': '^0.21.0',
                'formik': '^2.1.0',
                'lodash': '^4.17.0',
                'luxon': '^1.23.0',
                'path': '^0.12.0',
                'prop-types': '^15.7.0',
                'qs': '^6.9.0',
                'react': '^16.13.0',
                'react-dom': '^16.13.0',
                'react-redux': '^7.2.0',
                'react-searchkit': '^1.0.0-alpha.12',
                'redux': '^4.0.0',
                'redux-thunk': '^2.3.0',
                'semantic-ui-css': '^2.4.0',
                'semantic-ui-react': '^2.1.0',
                'yup': '^0.28.0',
            }
        ),
    }
)
