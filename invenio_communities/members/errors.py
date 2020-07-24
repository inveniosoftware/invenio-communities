# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community records errors."""

from ..errors import CommunitiesError


class CommunityMemberAlreadyExists(CommunitiesError):
    """Community membership already exists error."""

    def __init__(self, user_id, pid_id, invitation_id):
        """Initialize Exception."""
        self.user_id = user_id
        self.pid_id = pid_id
        self.invitation_id = invitation_id
