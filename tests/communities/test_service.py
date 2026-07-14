# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C) 2022 Northwestern University.
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community resources tests."""

import pytest

from flask_principal import AnonymousIdentity, Identity, Need, UserNeed
from invenio_accounts.testutils import create_test_user
from invenio_communities import current_communities

@pytest.fixture(scope="module")
def community_owner(app):
    """Community owner user."""
    return create_test_user('community-owner@inveniosoftware.org')


@pytest.fixture(scope="module")
def community_owner_identity(community_owner):
    """Simple identity fixture."""
    owner_id = community_owner.id
    i = Identity(owner_id)
    i.provides.add(UserNeed(owner_id))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="function")
def community_service(app, location):
    """Community service.

    Snuck in the location fixture, because needed on community creation
    i.e. almost every time this service is used.
    """
    return current_communities.service


@pytest.fixture()
def number_errors(community_service, community_owner_identity):
    """Number error fixture."""
    def _number_errors(communities):
        """Return number of errors creating communities."""
        errors = 0
        for input_community in communities:
            try:
                community_service.create(
                    community_owner_identity, data=input_community
                )
            except:
                errors += 1
        return errors

    return _number_errors


@pytest.fixture()
def invalid_community_input():
    """Valid community inpute fixture 2."""
    return {
        "access": {
            "visibility": "restricted",
            "member_policy": "closed",
            "record_policy": "closed",
        },
        "id": "id-with-&",
        "metadata": {
            "title": "Invalid & invalid",
            "type": "topic"
        }
    }

@pytest.fixture()
def valid_community_input_1():
    """Valid community inpute fixture 1."""
    return {
        "access": {
            "visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
        },
        "id": "good-community-1",
        "metadata": {
            "title": "Good community 1",
            "type": "project"
        }
    }


@pytest.fixture()
def valid_community_input_2():
    """Valid community inpute fixture 2."""
    return {
        "access": {
            "visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
        },
        "id": "good-community-2",
        "metadata": {
            "title": "Good community 2",
            "type": "project"
        }
    }


def test_create_multiple_communities_order_1(
        app, location,
        invalid_community_input, valid_community_input_1,
        valid_community_input_2, number_errors):
    """Problematic case."""

    communities = [
        valid_community_input_1,
        invalid_community_input,
        valid_community_input_2
    ]

    assert 1 == number_errors(communities)


def test_create_multiple_communities_order_2(
        app, location,
        invalid_community_input, valid_community_input_1,
        valid_community_input_2, number_errors):
    """Problematic case."""

    communities = [
        invalid_community_input,
        valid_community_input_1,
        valid_community_input_2
    ]

    # Expect the same results as above but it doesn't happen!
    assert 1 == number_errors(communities)
