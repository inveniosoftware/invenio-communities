# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test subcommunities workflows."""

import pytest
from invenio_access.permissions import system_identity
from invenio_requests.proxies import current_requests_service

from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities


@pytest.fixture(scope="module")
def subcommunity_service():
    """Return the subcommunity service."""
    return current_communities.subcommunity_service


@pytest.fixture(scope="module")
def curator(users):
    """Return the curator user."""
    return users["curator"]


@pytest.fixture(scope="module")
def create_community(location, community_service):
    """Return a factory to create a community."""

    def _create_community(owner, metadata, allow_children=False):
        """Create a community."""
        c = community_service.create(owner.identity, metadata)
        if allow_children:
            c._record.children.allow = True
        c._record.commit()
        Community.index.refresh()
        owner.refresh()
        return c

    return _create_community


def test_request():
    assert True


def test_service_join_already_existing(
    app,
    db,
    curator,
    owner,
    create_community,
    subcommunity_service,
    minimal_community,
    full_community,
):
    """Test joining a community with an existing subcommunity."""
    request_creator = curator
    request_receiver = owner
    del full_community["metadata"]["type"]

    parent_community = create_community(
        request_receiver, full_community, allow_children=True
    )
    child_community = create_community(request_creator, minimal_community)
    result = subcommunity_service.join(
        request_creator.identity,
        str(parent_community.id),
        {"community_id": str(child_community.id)},
    )
    request_obj = result._record
    assert request_obj.status == "submitted"

    # Test accept
    current_requests_service.execute_action(
        request_receiver.identity, id_=request_obj.id, action="accept"
    )
    req_read = current_requests_service.read(request_receiver.identity, request_obj.id)
    assert req_read._request.status == "accepted"


def test_service_join_with_new_community(parent_community, child_community, db):
    assert True
