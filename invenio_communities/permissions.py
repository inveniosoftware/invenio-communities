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

"""Permissions for communities."""
from functools import partial
from flask_login import current_user
from flask_principal import ActionNeed
from invenio_access.permissions import (DynamicPermission,
                                        ParameterizedActionNeed)


CommunityCreateActionNeed = partial(ActionNeed, 'communities-create')
"""Action need for reading a community."""

communities_create = CommunityCreateActionNeed()
"""Read communities action need."""

def create_permission_factory():
    """Factory for creating create permissions for communities."""
    return DynamicPermission(CommunityCreateActionNeed())

CommunityReadActionNeed = partial(ParameterizedActionNeed, 'communities-read')
"""Action need for reading a community."""

communities_read = CommunityReadActionNeed(None)
"""Read communities action need."""

def read_permission_factory(community):
    """Factory for creating read permissions for communities."""
    return DynamicPermission(CommunityReadActionNeed(str(community.id)))

CommunityEditActionNeed = partial(ParameterizedActionNeed, 'communities-edit')
"""Action need for editing a community."""

communities_edit = CommunityEditActionNeed(None)
"""Edit communities action need."""

def edit_permission_factory(community):
    """Factory for creating edit permissions for communities."""
    return DynamicPermission(CommunityEditActionNeed(str(community.id)))

CommunityDeleteActionNeed = partial(ParameterizedActionNeed, 'communities-delete')
"""Action need for deleting a community."""

communities_delete = CommunityDeleteActionNeed(None)
"""Delete communities action need."""

def delete_permission_factory(community):
    """Factory for creating delete permissions for communities."""
    return DynamicPermission(CommunityDeleteActionNeed(str(community.id)))

CommunityCurateActionNeed = partial(ParameterizedActionNeed, 'communities-curate')
"""Action need for editing a community."""

communities_curate = CommunityCurateActionNeed(None)
"""Curate communities action need."""

def curate_permission_factory(community):
    """Factory for creating curate permissions for communities."""
    return DynamicPermission(CommunityCurateActionNeed(str(community.id)))

CommunityTeamActionNeed = partial(ParameterizedActionNeed, 'communities-team-management')
"""Action need for team management in a community."""

communities_team = CommunityTeamActionNeed(None)
"""Team management communities action need."""

def team_permission_factory(community):
    """Factory for creating curate permissions for communities."""
    return DynamicPermission(CommunityTeamActionNeed(str(community.id)))
