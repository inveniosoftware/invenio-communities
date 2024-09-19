# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
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


@pytest.fixture()
def parent_community(db, create_community, owner, minimal_community):
    """Create and return a parent community."""
    return create_community(
        owner,
        {
            **minimal_community,
            "metadata": {"title": "Parent Community"},
            "slug": "parent-community",
        },
        allow_children=True,
    )


@pytest.fixture()
def child_community(db, create_community, curator, minimal_community):
    """Create and return a child community."""
    return create_community(
        curator,
        {
            **minimal_community,
            "metadata": {"title": "Child Community"},
            "slug": "child-community",
        },
    )


def test_service_join_already_existing(
    app,
    db,
    curator,
    owner,
    parent_community,
    child_community,
    subcommunity_service,
):
    """Test joining a community with an existing subcommunity."""
    request_creator = curator
    request_receiver = owner

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
    parent_community,
):
    """Test joining a community with a new subcommunity."""
    request_creator = curator
    request_receiver = owner
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
    app,
    db,
    owner,
    curator,
    reader,
    parent_community,
    child_community,
):
    """Test joining with a subcommunity not owned by the user."""
    payload = {"community_id": str(child_community.id)}
    with pytest.raises(PermissionDeniedError):
        current_communities.subcommunity_service.join(
            reader.identity,
            str(parent_community.id),
            payload,
        )


# Resource tests
def test_subcommunity_simple_flow(app, curator, owner, parent_community):
    """Test the basic workflow for a subcommunity request."""
    client = curator.login(app.test_client())
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
    request_id = res.json["id"]
    new_community_id = res.json["topic"]["community"]
    assert res.json == {
        "id": request_id,
        "number": res.json["number"],
        "created_by": {"community": new_community_id},
        "topic": {"community": new_community_id},
        "receiver": {"community": str(parent_community.id)},
        "type": "subcommunity",
        "status": "submitted",
        "title": 'Inclusion of subcommunity "Test community"',
        "created": res.json["created"],
        "updated": res.json["updated"],
        "expires_at": None,
        "revision_id": 2,
        "is_closed": False,
        "is_expired": False,
        "is_open": True,
        "links": {
            "actions": {
                # The requester can only cancel the request
                "cancel": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/cancel",
            },
            "comments": f"https://127.0.0.1:5000/api/requests/{request_id}/comments",
            "self": f"https://127.0.0.1:5000/api/requests/{request_id}",
            "self_html": f"https://127.0.0.1:5000/requests/{request_id}",
            "timeline": f"https://127.0.0.1:5000/api/requests/{request_id}/timeline",
        },
    }

    # Check the new community
    res = client.get(
        f"/communities/{new_community_id}",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["id"] == new_community_id
    assert res.json["metadata"]["title"] == "Test community"
    assert res.json["slug"] == "test-community"

    # Accept the request as the parent community owner
    client = owner.login(app.test_client())
    res = client.get(
        f"/requests/{request_id}",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["links"]["actions"] == {
        # The parent community owner can accept or decline the request
        "accept": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/accept",
        "decline": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/decline",
    }

    res = client.post(
        f"/requests/{request_id}/actions/accept",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["status"] == "accepted"
    assert res.json == {
        "id": request_id,
        "number": res.json["number"],
        "created_by": {"community": new_community_id},
        "topic": {"community": new_community_id},
        "receiver": {"community": str(parent_community.id)},
        "created": res.json["created"],
        "updated": res.json["updated"],
        "expires_at": None,
        "type": "subcommunity",
        "status": "accepted",
        "title": 'Inclusion of subcommunity "Test community"',
        "revision_id": 3,
        "is_closed": True,
        "is_expired": False,
        "is_open": False,
        "links": {
            "actions": {},
            "comments": f"https://127.0.0.1:5000/api/requests/{request_id}/comments",
            "self": f"https://127.0.0.1:5000/api/requests/{request_id}",
            "self_html": f"https://127.0.0.1:5000/requests/{request_id}",
            "timeline": f"https://127.0.0.1:5000/api/requests/{request_id}/timeline",
        },
    }

    # Check that the child community is a subcommunity of the parent community
    res = client.get(
        f"/communities/{new_community_id}",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["parent"]["id"] == str(parent_community.id)

    Community.index.refresh()

    res = client.get(
        f"/communities/{parent_community.id}/subcommunities",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1


def test_subcommunity_existing_child_flow(
    app, curator, owner, parent_community, child_community
):
    """Test the subcommunity request workflow for an existing community."""
    # Create a request
    client = curator.login(app.test_client())
    res = client.post(
        f"/communities/{str(parent_community.id)}/actions/join-request",
        json={"community_id": str(child_community.id)},
        headers={"content-type": "application/json"},
    )

    assert res.status_code == 201
    request_id = res.json["id"]
    assert res.json == {
        "id": request_id,
        "number": res.json["number"],
        "created_by": {"community": str(child_community.id)},
        "topic": {"community": str(child_community.id)},
        "receiver": {"community": str(parent_community.id)},
        "type": "subcommunity",
        "status": "submitted",
        "title": 'Inclusion of subcommunity "Child Community"',
        "created": res.json["created"],
        "updated": res.json["updated"],
        "expires_at": None,
        "revision_id": 2,
        "is_closed": False,
        "is_expired": False,
        "is_open": True,
        "links": {
            "actions": {
                # The requester can only cancel the request
                "cancel": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/cancel",
            },
            "comments": f"https://127.0.0.1:5000/api/requests/{request_id}/comments",
            "self": f"https://127.0.0.1:5000/api/requests/{request_id}",
            "self_html": f"https://127.0.0.1:5000/requests/{request_id}",
            "timeline": f"https://127.0.0.1:5000/api/requests/{request_id}/timeline",
        },
    }

    # Accept the request as the parent community owner
    client = owner.login(app.test_client())
    res = client.get(
        f"/requests/{request_id}",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["links"]["actions"] == {
        # The parent community owner can accept or decline the request
        "accept": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/accept",
        "decline": f"https://127.0.0.1:5000/api/requests/{request_id}/actions/decline",
    }

    res = client.post(
        f"/requests/{request_id}/actions/accept",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["status"] == "accepted"
    assert res.json == {
        "id": request_id,
        "number": res.json["number"],
        "created_by": {"community": str(child_community.id)},
        "topic": {"community": str(child_community.id)},
        "receiver": {"community": str(parent_community.id)},
        "created": res.json["created"],
        "updated": res.json["updated"],
        "expires_at": None,
        "type": "subcommunity",
        "status": "accepted",
        "title": 'Inclusion of subcommunity "Child Community"',
        "revision_id": 3,
        "is_closed": True,
        "is_expired": False,
        "is_open": False,
        "links": {
            "actions": {},
            "comments": f"https://127.0.0.1:5000/api/requests/{request_id}/comments",
            "self": f"https://127.0.0.1:5000/api/requests/{request_id}",
            "self_html": f"https://127.0.0.1:5000/requests/{request_id}",
            "timeline": f"https://127.0.0.1:5000/api/requests/{request_id}/timeline",
        },
    }

    # Check that the child community is a subcommunity of the parent community
    res = client.get(
        f"/communities/{str(child_community.id)}",
        headers={"content-type": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["parent"]["id"] == str(parent_community.id)
