# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permissions for communities."""

from __future__ import absolute_import, print_function

from flask_login import current_user
from flask_principal import ActionNeed
from invenio_access.permissions import Permission


class _Permission(object):
    """Temporary solution to permissions.

    Grant access to owners of community or admin.
    TODO: Use fine-grained permissions.
    """

    def __init__(self, community, action):
        """Initialize."""
        self.community = community
        self.action = action

    def can(self):
        """Grant permission if owner or admin."""
        return str(current_user.get_id()) == str(self.community.id_user) or \
            Permission(ActionNeed('admin-access')).can()


def permission_factory(community, action):
    """Permission factory for the actions on Bucket and ObjectVersion items.

    :param community: Community object to be accessed.
    :type community: `invenio_communities.models.Community`
    :param action: Action name for access.
    :type action: str
    """
    return _Permission(community, action)
