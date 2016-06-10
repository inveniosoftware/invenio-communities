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


CommunityAdminActionNeed = partial(ParameterizedActionNeed, 'communities-admin')
"""Action need for create or delete a community."""

communities_admin = CommunityAdminActionNeed(None)
"""Admin communities action need."""

def admin_permission_factory(community=""):
    """Factory for creating admin permissions for communities."""
    return DynamicPermission(CommunityAdminActionNeed(None))

CommunityReadActionNeed = partial(ParameterizedActionNeed, 'communities-read')
"""Action need for reading a community."""

communities_read = CommunityReadActionNeed(None)
"""Read communities action need."""

def read_permission_factory(community):
    """Factory for creating read permissions for communities."""
    return DynamicPermission(CommunityReadActionNeed(str(community.id)))

CommunityManageActionNeed = partial(ParameterizedActionNeed, 'communities-manage')
"""Action need for editing or manage team of a community."""

communities_manage = CommunityManageActionNeed(None)
"""Manage communities action need."""

def manage_permission_factory(community):
    """Factory for creating manage permissions for communities."""
    return DynamicPermission(CommunityManageActionNeed(str(community.id)))

CommunityCurateActionNeed = partial(ParameterizedActionNeed, 'communities-curate')
"""Action need for editing a community."""

communities_curate = CommunityCurateActionNeed(None)
"""Curate communities action need."""

def curate_permission_factory(community):
    """Factory for creating curate permissions for communities."""
    return DynamicPermission(CommunityCurateActionNeed(str(community.id)))
