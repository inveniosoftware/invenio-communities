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
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "invenio-communities-new": "./js/invenio_communities/community/new.js",
                "invenio-communities-privileges": "./js/invenio_communities/settings/privileges.js",
                "invenio-communities-profile": "./js/invenio_communities/settings/profile/index.js",
                "invenio-communities-requests": "./js/invenio_communities/requests/index.js",
                "invenio-communities-frontpage": "./js/invenio_communities/community/frontpage.js",
                "invenio-communities-details-search": "./js/invenio_communities/details_search/index.js",
                "invenio-communities-search": "./js/invenio_communities/community/search.js",
                "invenio-communities-members": "./js/invenio_communities/members/members/member_view/index.js",
                "invenio-communities-members-manager": "./js/invenio_communities/members/members/manager_view/index.js",
                "invenio-communities-members-public": "./js/invenio_communities/members/members/public_view/index.js",
                "invenio-communities-invitations": "./js/invenio_communities/members/invitations/index.js",
            },
            dependencies={
                "@ckeditor/ckeditor5-build-classic": "^16.0.0",
                "@ckeditor/ckeditor5-react": "^2.1.0",
                "@semantic-ui-react/css-patch": "^1.0.0",
                "react-router-dom": "^6.3.0",
                "react-invenio-forms": "^0.10.0",
                "react-invenio-deposit": "^0.19.15",
                "axios": "^0.21.0",
                "formik": "^2.1.0",
                "i18next": "^20.3.0",
                "i18next-browser-languagedetector": "^6.1.0",
                "lodash": "^4.17.0",
                "luxon": "^1.23.0",
                "path": "^0.12.0",
                "prop-types": "^15.7.0",
                "qs": "^6.9.0",
                "react": "^16.13.0",
                "react-dom": "^16.13.0",
                "react-i18next": "^11.11.0",
                "react-redux": "^7.2.0",
                "react-searchkit": "^2.0.0",
                "redux": "^4.0.0",
                "redux-thunk": "^2.3.0",
                "semantic-ui-css": "^2.4.0",
                "semantic-ui-react": "^2.1.0",
                "yup": "^0.28.0",
            },
            aliases={
                # Define Semantic-UI theme configuration needed by
                # Invenio-Theme in order to build Semantic UI (in theme.js
                # entry point). theme.config itself is provided by
                # cookiecutter-invenio-rdm.
                "@js/invenio_communities": "js/invenio_communities",
                "@translations/invenio_communities": "translations/invenio_communities",
            },
        ),
    },
)
