# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import itertools
from copy import deepcopy

import pytest
from flask_principal import AnonymousIdentity
from invenio_access.permissions import any_user as any_user_need
from invenio_accounts.models import Role
from invenio_app.factory import create_api
from invenio_requests.proxies import current_events_service, current_requests_service

from invenio_communities.communities.records.api import Community
from invenio_communities.proxies import current_communities

pytest_plugins = ("celery.contrib.pytest", )


#
# Application
#
@pytest.fixture(scope='module')
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    app_config['RECORDS_REFRESOLVER_CLS'] = \
        "invenio_records.resolver.InvenioRefResolver"
    app_config['RECORDS_REFRESOLVER_STORE'] = \
        "invenio_jsonschemas.proxies.current_refresolver_store"
    # Variable not used. We set it to silent warnings
    app_config['JSONSCHEMAS_HOST'] = 'not-used'

    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        'content-type': 'application/json',
        'accept': 'application/json',
    }


#
# Services
#
@pytest.fixture(scope="module")
def community_service(app):
    """Community service."""
    return current_communities.service


@pytest.fixture(scope="module")
def member_service(community_service):
    """Members subservice."""
    return community_service.members


@pytest.fixture(scope="module")
def requests_service(app):
    """Requests service."""
    return current_requests_service


@pytest.fixture(scope="module")
def events_service(app):
    """Requests service."""
    return current_events_service


#
# Users and groups
#
@pytest.fixture(scope="module")
def anon_identity():
    """A new user."""
    identity = AnonymousIdentity()
    identity.provides.add(any_user_need)
    return identity


@pytest.fixture(scope="module")
def users(UserFixture, app, database):
    users = {}
    for r in ['owner', 'manager', 'curator', 'reader']:
        u = UserFixture(
            email=f'{r}@{r}.org',
            password=r,
        )
        u.create(app, database)
        users[r] = u
    return users


@pytest.fixture(scope="module")
def group(database):
    r = Role(name='it-dep')
    database.session.add(r)
    database.session.commit()
    return r


@pytest.fixture(scope="module")
def owner(users):
    """Community owner user."""
    return users['owner']


@pytest.fixture(scope="module")
def any_user(UserFixture, app, database):
    """A user without privileges or memberships."""
    u = UserFixture(
        email=f'anyuser@anyuser.org',
        password='anyuser',
    )
    u.create(app, database)
    u.identity # compute identity
    return u


#
# Communities
#
@pytest.fixture(scope="module")
def minimal_community():
    """Minimal community metadata."""
    return  {
        "access": {
            "visibility": "public",
            "record_policy": "open",
        },
        "id": "public",
        "metadata": {
            "title": "My Community",
        }
    }

@pytest.fixture(scope="module")
def full_community():
    """Full community data as dict coming from the external world."""
    return  {
        "access": {
            "visibility": "public",
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
            "organizations": [{
                    "name": "CERN",
            }]
        }
    }


@pytest.fixture(scope="module")
def community(community_service, owner, minimal_community, location):
    """A community."""
    c =  community_service.create(owner.identity, minimal_community)
    owner.refresh()
    return c


@pytest.fixture(scope="module")
def restricted_community(community_service, owner, minimal_community, location):
    """A restricted community."""
    data = deepcopy(minimal_community)
    data['access']['visibility'] = 'restricted'
    data['id'] = 'restricted'
    c =  community_service.create(owner.identity, data)
    owner.refresh()
    return c


@pytest.fixture(scope="function")
def fake_communities(community_service, owner, minimal_community, location, db):
    """Multiple community created and posted to test search functionality."""
    community_types = ['organization', 'event', 'topic', 'project']

    N = 4
    for (type_,ind) in itertools.product(community_types, list(range(N))):
        minimal_community['id'] = f'comm_{type_}_{ind}'
        minimal_community['metadata']['type'] = type_
        c =  community_service.create(owner.identity, minimal_community)
    Community.index.refresh()

    # Return ids of first and last created communities
    return 'comm_organization_0', 'comm_project_3', N, N*len(community_types)
