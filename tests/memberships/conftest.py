# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from copy import deepcopy

import pytest
from flask_principal import AnonymousIdentity, Identity, Need, UserNeed
from invenio_accounts.testutils import create_test_user
from invenio_access import any_user, authenticated_user
from invenio_communities.permissions import create_community_role_need

from invenio_communities.proxies import current_communities


@pytest.fixture(scope="function")
def community_service(app, location):
    """Community service.

    Snuck in the location fixture, because needed on community creation
    i.e. almost every time this service is used.
    """
    return current_communities.service


@pytest.fixture(scope="module")
def community_owner(app):
    """Community owner user."""
    return create_test_user('community-owner@inveniosoftware.org')


@pytest.fixture(scope="module")
def community_creation_input_data():
    """Full community data used as input to community service."""
    return  {
        "access": {
            "visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
        },
        "id": "my_community_id",
        "metadata": {
            "title": "My Community",
            "description": "This is an example Community.",
            "type": "event",
            "curation_policy": "This is the kind of records we accept.",
            "website": "https://inveniosoftware.org/",
            "organizations": [{
                    "name": "CERN",
            }]
        }
    }


@pytest.fixture(scope="module")
def user1(app):
    """Just a user."""
    return create_test_user('user1@inveniosoftware.org')


# Identities

@pytest.fixture(scope="module")
def community_owner_identity(community_owner):
    """Simple identity fixture."""
    owner_id = community_owner.id
    i = Identity(owner_id)
    i.provides.add(UserNeed(owner_id))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="module")
def anyuser_identity():
    """Anyone identity."""
    identity = AnonymousIdentity()
    identity.provides.add(any_user)
    return identity


@pytest.fixture(scope="module")
def create_user_identity(app):
    """Create a user and return their identity."""

    def _create_user_identity(email):
        """Create identity."""
        user = create_test_user(email)
        identity = Identity(user.id)
        identity.provides.add(UserNeed(user.id))
        identity.provides.add(any_user)
        identity.provides.add(authenticated_user)
        return identity

    return _create_user_identity


@pytest.fixture(scope="module")
def make_member_identity():
    """Create a community member+role identity."""

    def _make_member_identity(identity, community, role=None):
        """Create new identity from identity."""
        i = deepcopy(identity)
        i.provides.add(create_community_role_need(community.id, "member"))

        if role:
            i.provides.add(create_community_role_need(community.id, role))

        return i

    return _make_member_identity


@pytest.fixture(scope="module")
def create_community_identity(create_user_identity, make_member_identity):
    """Create a community identity."""
    i = 0

    def _create_community_identity(community, role):
        """Creating function."""
        nonlocal i  # Needed to close over i
        identity = create_user_identity(f"{i}@example.com")
        identity = make_member_identity(identity, community, role)
        i += 1
        return identity

    return _create_community_identity


@pytest.fixture()
def generate_invitation_input_data():
    """Generate invitation data used as input to invitation service."""

    def _generate_invitation_input_data(
            community_uuid, entity_dict, role="reader"):
        return {
            "type": "community-member-invitation",
            "receiver": entity_dict,
            "payload": {
                "role": role,
            },
            # Added by resource
            "topic": {'community': str(community_uuid)}
        }

    return _generate_invitation_input_data
