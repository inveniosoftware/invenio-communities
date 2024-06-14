# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Test subcommunities workflows."""

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
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
def reader(users):
    """Return the reader user."""
    return users["reader"]


@pytest.fixture(scope="module")
def full_community(full_community):
    """Return a full community."""
    del full_community["metadata"]["type"]
    return full_community


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


def test_service_join_already_existing(
    app,
    db,
    curator,
    owner,
    reader,
    create_community,
    subcommunity_service,
    minimal_community,
    full_community,
):
    """Test joining a community with an existing subcommunity."""
    request_creator = curator
    request_receiver = owner

    parent_community = create_community(
        request_receiver, full_community, allow_children=True
    )
    child_community = create_community(curator, minimal_community)
    payload = {"community_id": str(child_community.id)}
    result = subcommunity_service.join(
        request_creator.identity,
        str(parent_community.id),
        payload,
    )
    request_obj = result._record
    assert request_obj.status == "submitted"

    # Test accept
    current_requests_service.execute_action(
        request_receiver.identity, id_=request_obj.id, action="accept"
    )
    req_read = current_requests_service.read(request_receiver.identity, request_obj.id)
    assert req_read._request.status == "accepted"
    assert str(request_obj.topic.resolve().parent.id) == parent_community.id


def test_service_join_with_new_community(
    app,
    db,
    curator,
    owner,
    create_community,
    full_community,
):
    """Test joining a community with a new subcommunity."""
    request_creator = curator
    request_receiver = owner
    parent_community = create_community(
        request_receiver, full_community, allow_children=True
    )
    payload = {
        "community": {
            "title": "Test community",
            "slug": "test-community",
        }
    }
    result = current_communities.subcommunity_service.join(
        request_creator.identity,
        str(parent_community.id),
        payload,
    )
    request_obj = result._record
    assert request_obj.status == "submitted"

    # Test accept
    current_requests_service.execute_action(
        request_receiver.identity, id_=request_obj.id, action="accept"
    )
    req_read = current_requests_service.read(system_identity, request_obj.id)
    assert req_read._request.status == "accepted"
    assert str(request_obj.topic.resolve().parent.id) == parent_community.id


def test_service_join_permissions(
    app, db, owner, curator, reader, create_community, full_community, minimal_community
):
    """Test joining with a subcommunity not owned by the user."""
    parent_community = create_community(curator, full_community, allow_children=True)
    child_community = create_community(owner, minimal_community)
    payload = {"community_id": str(child_community.id)}
    with pytest.raises(PermissionDeniedError):
        current_communities.subcommunity_service.join(
            reader.identity,
            str(parent_community.id),
            payload,
        )


# Resource tests
def test_subcommunity_simple_flow(
    app, curator, owner, create_community, minimal_community
):
    """Test the basic workflow for a subcommunity request."""
    client = owner.login(app.test_client())
    parent_community = create_community(owner, minimal_community, allow_children=True)
    payload = {
        "community": {
            "title": "Test community",
            "slug": "test-community",
        }
    }
    # Create a request
    res = client.post(
        f"/communities/{str(parent_community.id)}/actions/join-request",
        json=payload,
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 201

    # Accept the request
    request_id = res.json["id"]
    res = client.post(
        f"/requests/{request_id}/actions/accept",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["status"] == "accepted"
    # TODO created community ID is not returned in the response yet
