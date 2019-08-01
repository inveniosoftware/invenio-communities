# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Communities bundles."""

from __future__ import absolute_import, print_function

from flask_assets import Bundle
from invenio_assets import NpmBundle, RequireJSFilter

js = Bundle(
    "js/invenio_communities/main.js",
    filters=RequireJSFilter(),
    output='gen/communities.%(version)s.js'
)

ckeditor = Bundle(
    "js/invenio_communities/ckeditor.js",
    filters=RequireJSFilter(),
    output='gen/communities.%(version)s.js'
)

css = NpmBundle(
    'scss/invenio_communities/communities.scss',
    filters='scss, cleancss',
    output='gen/communities.%(version)s.css',
    npm={
        'ckeditor': '~4.5.8',
    }
)
