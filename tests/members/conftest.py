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

from invenio_communities.members.records.api import ArchivedInvitation, Member


#
# Module scoped
#
@pytest.fixture(scope="module")
def new_user(UserFixture, app, database):
    """A new user."""
    u = UserFixture(
        email=f'newuser@newuser.org',
        password='newuser',
        user_profile={
            'full_name': 'New User',
            'affiliations': 'CERN',
        },
        preferences={
            'visibility': 'public',
            'email_visibility': 'restricted',
        },
        active=True,
        confirmed=True
    )
    u.create(app, database)
    return u


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
    list(current_search.delete(index_list=[
        Request.index._name,
        Member.index._name,
        ArchivedInvitation.index._name,
    ]))
    list(current_search.create(index_list=[
        Request.index._name,
        Member.index._name,
        ArchivedInvitation.index._name,
    ]))
    member_service.rebuild_index(system_identity)
    requests_service.rebuild_index(system_identity)
    Member.index.refresh()
    Request.index.refresh()
    ArchivedInvitation.index.refresh()
    return True


@pytest.fixture(scope="function")
def members(member_service, community, users, db):
    for name, user in users.items():
        if name == 'owner':
            continue
        m = Member.create(
            {},
            community_id=community._record.id,
            user_id=user.id,
            role=name,
            visible=False,
            active=True,
        )
        member_service.indexer.index(m)
        Member.index.refresh()
    db.session.commit()
    return users


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
        receiver={'user': invite_user.id},
        type='community-invitation',
    ).to_dict()
    return res['hits']['hits'][0]['id']
