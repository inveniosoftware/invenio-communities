
# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community records errors."""


class CommunityRecordError(Exception):
    """Community record base error class."""

    def __init__(self, community_pid_id, record_pid_id):
        """Initialize Exception."""
        self.community_pid_id = community_pid_id
        self.record_pid_id = record_pid_id


class CommunityRecordAlreadyExists(CommunityRecordError):
    """Record inclusion already exists error."""


class CommunityRecordDoesNotExist(CommunityRecordError):
    """Record inclusion does not exist error."""
