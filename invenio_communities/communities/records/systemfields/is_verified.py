# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Record 'verified' system field."""

from invenio_records_resources.records.systemfields.calculated import CalculatedField


class IsVerifiedField(CalculatedField):
    """Systemfield for calculating whether or not the request is expired."""

    def __init__(self, key=None):
        """Constructor."""
        super().__init__(key=key, use_cache=False)

    def calculate(self, record):
        """Calculate the ``is_verified`` property of the record."""
        # import here due to circular import
        from invenio_communities.members.records.api import Member

        community_verified = False
        owners = [m.dumps() for m in Member.get_members(record.id) if m.role == "owner"]
        for owner in owners:
            # community is considered verified if at least one owner is verified
            if owner["user"]["verified_at"] is not None:
                community_verified = True
                break
        return community_verified
