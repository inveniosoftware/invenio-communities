# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_access.permissions import system_identity
from invenio_requests.records.api import Request
from invenio_search import current_search
from invenio_users_resources.proxies import current_users_service

from invenio_communities.members.records.api import ArchivedInvitation, Member


#
# Function scope
#
@pytest.fixture(scope="function")
def clean_index(member_service, requests_service, db):
    """Clean the member and request index to match database state.

    Use this function when your tests depends on having a clean index
    state. This is an "expensive" fixture to run, thus only use it if your
    tests really doesn't work without.
    """
    list(
        current_search.delete(
            index_list=[
                Request.index._name,
                Member.index._name,
                ArchivedInvitation.index._name,
            ]
        )
    )
    list(
        current_search.create(
            index_list=[
                Request.index._name,
                Member.index._name,
                ArchivedInvitation.index._name,
            ]
        )
    )
    member_service.rebuild_index(system_identity)
    requests_service.rebuild_index(system_identity)
    member_service.indexer.process_bulk_queue()
    requests_service.indexer.process_bulk_queue()
    Member.index.refresh()
    Request.index.refresh()
    ArchivedInvitation.index.refresh()
    return True


@pytest.fixture(scope="function")
def invite_user(member_service, community, owner, new_user, db):
    """An invited user."""
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
        "message": "Welcome to the club!",
    }
    member_service.invite(owner.identity, community._record.id, data)
    return new_user


@pytest.fixture(scope="function")
def public_reader(member_service, community, new_user, db):
    """Add a reader member with public visibility."""
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
        "visible": True,
    }
    member_service.add(system_identity, community._record.id, data)
    return new_user


@pytest.fixture(scope="function")
def invite_request_id(requests_service, invite_user):
    """An invitation request."""
    Request.index.refresh()
    res = requests_service.search(
        invite_user.identity,
        receiver={"user": invite_user.id},
        type="community-invitation",
    ).to_dict()
    return res["hits"]["hits"][0]["id"]


@pytest.fixture(scope="function")
def membership_request(member_service, community, create_user, db, search_clear):
    """A membership request."""
    user = create_user()
    data = {
        "message": "Can I join the club?",
    }
    return member_service.request_membership(
        user.identity,
        community._record.id,
        data,
    )
