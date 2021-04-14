# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import uuid

import pytest
from flask_security import login_user
from invenio_accounts.testutils import create_test_user, login_user_via_session
from invenio_app.factory import create_api


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
def minimal_community_record(community_owner):
    """Minimal community data as dict coming from the external world."""
    return {
        "id": "comm_id",
        "metadata": {
            "title": "Title",
            "type": "topic",
            "created_by": community_owner.id,
            "member_policy": "open"
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
