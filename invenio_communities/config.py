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

COMMUNITIES_REQUEST_EXPIRY_TIME = 7  # Default expiry time delta in days

COMMUNITIES_LOGO_EXTENSIONS = ['.png', '.jpg', '.jpeg']
"""Allowed file extensions for the communities logo."""

COMMUNITIES_RECORD_KEY = 'communities'
"""Key inside the JSON record for communities."""

COMMUNITIES_SORTING_OPTIONS = [
    'title',
    'ranking',
]
"""Possible communities sorting options."""

COMMUNITIES_DEFAULT_SORTING_OPTION = 'ranking'
