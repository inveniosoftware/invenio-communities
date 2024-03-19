# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test safelist feature for communities."""

from copy import deepcopy

from invenio_db import db

from invenio_communities.communities.records.systemfields.community_status import (
    CommunityStatusEnum,
)


def test_safelist_computed_by_verified_status(
    community_service, minimal_community, location, es_clear, unverified_user
):
    """Test that the safelist feature for communities is computed correctly based on the verified status."""
    # Create a comunity
    # Flag it as "verified"
    # Validate that the computed field "is_verified" is set to "True"
    c_data = deepcopy(minimal_community)
    c_data["slug"] = "test_status_perms"
    c_item = community_service.create(unverified_user.identity, data=c_data)
    assert c_item._record.status == CommunityStatusEnum.NEW
    assert c_item._record.is_safelisted is False
    community = community_service.record_cls.pid.resolve(c_item.id)
    community.status = CommunityStatusEnum.VERIFIED
    community.commit()
    db.session.commit()
    c_item = community_service.read(unverified_user.identity, c_item.id)
    assert c_item._record.is_safelisted is True
