# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Record 'verified' system field."""

from invenio_records_resources.records.systemfields.calculated import (
    CalculatedIndexedField,
)


class IsVerifiedField(CalculatedIndexedField):
    """Systemfield for calculating whether or not the request is expired."""

    def __init__(self, key=None, **kwargs):
        """Constructor."""
        super().__init__(key=key, **kwargs)

    def calculate(self, record):
        """Calculate the ``is_verified`` property of the record."""
        # import here due to circular import
        from invenio_communities.members.records.api import Member

        owners = [m.dumps() for m in Member.get_members(record.id) if m.role == "owner"]

        # community is considered verified if at least one owner is verified
        # a user is verified if verified_at is not None
        for owner in owners:
            if "user" in owner and owner["user"]["verified_at"] is not None:
                return True

        return False
