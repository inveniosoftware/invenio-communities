# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Proxy definitions."""

from __future__ import absolute_import, print_function

from flask import current_app
from werkzeug.local import LocalProxy

from .permissions import (CommunityCreateActionNeed,
                          CommunityReadActionNeed,
                          CommunityEditActionNeed,
                          CommunityDeleteActionNeed,
                          CommunityCurateActionNeed,
                          CommunityTeamActionNeed)

current_permission_factory = {
    "communities-create": LocalProxy(lambda:
        current_app.extensions["invenio-communities"].create_permission_factory),
    "communities-read": LocalProxy(lambda:
        current_app.extensions["invenio-communities"].read_permission_factory),
    "communities-edit": LocalProxy(lambda:
        current_app.extensions["invenio-communities"].edit_permission_factory),
    "communities-delete": LocalProxy(lambda:
        current_app.extensions["invenio-communities"].delete_permission_factory),
    "communities-curate": LocalProxy(lambda:
        current_app.extensions["invenio-communities"].curate_permission_factory),
    "communities-team-management": LocalProxy(lambda:
        current_app.extensions["invenio-communities"].team_permission_factory)
}

needs = {
    "communities-create": CommunityCreateActionNeed,
    "communities-read": CommunityReadActionNeed,
    "communities-edit": CommunityEditActionNeed,
    "communities-delete": CommunityDeleteActionNeed,
    "communities-curate": CommunityCurateActionNeed,
    "communities-team-management": CommunityTeamActionNeed
}
