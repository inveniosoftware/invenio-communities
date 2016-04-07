# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

"""Invenio Communities configuration."""

from __future__ import unicode_literals

import pkg_resources

COMMUNITIES_REQUEST_EXPIRY_TIME = 7  # Default expiry time delta in days

COMMUNITIES_LOGO_EXTENSIONS = ['png', 'jpg', 'jpeg']
"""Allowed file extensions for the communities logo."""

COMMUNITIES_RECORD_KEY = 'communities'
"""Key inside the JSON record for communities."""

COMMUNITIES_SORTING_OPTIONS = [
    'title',
    'ranking',
]
"""Possible communities sorting options."""

COMMUNITIES_DEFAULT_SORTING_OPTION = 'ranking'
"""Default sorting option."""

COMMUNITIES_OAI_FORMAT = 'user-{community_id}'
"""String template for the community OAISet 'spec'."""

COMMUNITIES_OAI_ENABLED = False
"""Using OAIServer if available."""

COMMUNITIES_BUCKET_UUID = '00000000-0000-0000-0000-000000000000'
"""UUID for the bucket corresponding to communities."""

COMMUNITIES_INDEX_PREFIX = 'records-'
"""Key inside the JSON record for communities."""

try:
    pkg_resources.get_distribution('invenio_oaiserver')
    COMMUNITIES_OAI_ENABLED = True
except pkg_resources.DistributionNotFound:  # pragma: no cover
    pass

COMMUNITIES_JSTEMPLATE_RESULTS_CURATE = \
    'templates/invenio_communities/ng_record_curate.html'
