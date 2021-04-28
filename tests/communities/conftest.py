# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import itertools
import uuid

import pytest
from flask_security import login_user
from invenio_accounts.testutils import create_test_user, login_user_via_session
from invenio_app.factory import create_api

from invenio_communities.communities.records.api import Community


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope='module')
def users(app):
    yield [create_test_user('user{}@inveniosoftware.org'.format(i)) for i in range(3)]


@pytest.fixture
def authenticated_user(db):
    """Authenticated user."""
    yield create_test_user('authed@inveniosoftware.org')


@pytest.fixture
def community_owner(db):
    """Record owner user."""
    yield create_test_user('community-owner@inveniosoftware.org')


@pytest.fixture(scope="function")
def minimal_community(community_owner):
    """Minimal community data as dict coming from the external world."""
    return {
        "id": "comm_id",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "Title",
            "type": "topic"
        }
    }


@pytest.fixture(scope="function")
def full_community(community_owner):
    """Full community data as dict coming from the external world."""
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
            "page": "Information for my community.",
            "website": "https://inveniosoftware.org/",
            "funding":[{
                "funder": {
                    "name": "European Commission",
                    "identifier": "00k4n6c32",
                    "scheme": "ror"
                },
                "award": {
                    "title": "OpenAIRE",
                    "number": "246686",
                    "identifier": ".../246686",
                    "scheme": "openaire"
                }
            }],
            "organizations": [{
                    "name": "CERN",
                    "identifiers": [
                        {
                        "identifier": "01ggx4157",
                        "scheme": "ror"
                        }
                    ]
            }]
        }
    }


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        'content-type': 'application/json',
        'accept': 'application/json',
    }


@pytest.fixture()
def client_with_login(client, users):
    """Log in a user to the client."""
    user = users[0]
    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)
    return client


@pytest.fixture(scope="function")
def create_many_records(app, client_with_login, minimal_community, headers):
    """Multiple community created and posted to test search functionality."""
    client = client_with_login
    community_types = ['organization', 'event', 'topic', 'project']
    N = 4
    for (type_,ind) in itertools.product(community_types, list(range(N))):
        minimal_community['id'] = f'comm_{type_}_{ind}'
        minimal_community['metadata']['type'] = type_
        client.post( '/communities', headers=headers, json=minimal_community)

    Community.index.refresh()

    # Return ids of first and last created communities
    return 'comm_organization_0', 'comm_project_3', N, N*len(community_types)
