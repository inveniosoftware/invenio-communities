# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Communities bundles."""

from __future__ import absolute_import, print_function

from flask_assets import Bundle
from invenio_assets import NpmBundle, RequireJSFilter

js = NpmBundle(
    Bundle(
        "node_modules/almond/almond.js",
        "js/invenio_communities/main.js",
        filters=RequireJSFilter(),
    ),
    output='gen/communities.%(version)s.js',
    filters=RequireJSFilter(),
    depends=('node_modules/invenio-search-js/dist/*.js', ),
    npm={
        "almond": "~0.3.1",
        'angular': '~1.4.10',
        'angular-loading-bar': '~0.9.0',
        'invenio-search-js': '~0.1.6'
    },
)

jsselect = NpmBundle(
    "node_modules/jquery/jquery.min.js",
    "node_modules/bootstrap3/dist/js/bootstrap.min.js",
    "node_modules/select2/dist/js/select2.min.js",
    npm={
        "jquery": "~1.9.1",
        "bootstrap3": "~3.3.5",
        "select2": "~4.0.2"
    },
    output="gen/communities_select.%(version)s.js"
)

csselect = NpmBundle(
    "node_modules/select2/dist/css/select2.min.css",
    "node_modules/select2-bootstrap-css/select2-bootstrap.min.css",
    npm={
        "select2": "~4.0.2",
        "select2-bootstrap-css": "~1.4.6"
    },
    output="gen/communities_select.%(version)s.css"
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
