# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community permissions."""

from flask_security import current_user


def allow_logged_in(*args, **kwargs):
    """Permission that checks if the community owner is making the request."""
    def can(self):
        """Check that the current user is the community's owner."""
        return current_user.is_authenticated
    return type('AllowCommunityOwner', (), {'can': can})()



def allow_community_owner(record, *args, **kwargs):
    """Permission that checks if the community owner is making the request."""
    def can(self):
        """Check that the current user is the community's owner."""
        if current_user.is_authenticated:
            return current_user.id == record['created_by']
        return False
    return type('AllowCommunityOwner', (), {'can': can})()
