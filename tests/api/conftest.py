# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import uuid

import pytest
from invenio_accounts.testutils import create_test_user
from invenio_app.factory import create_api
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from invenio_communities.indexer import CommunityIndexer
from invenio_communities.proxies import Community


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


@pytest.fixture
def community(db, es, community_owner):
    """Community fixture."""
    community_id = str(uuid.uuid4())
    comid = PersistentIdentifier.create(
        pid_type='comid', pid_value='biosyslit',
        object_uuid=community_id, object_type='com',
        status=PIDStatus.REGISTERED)
    community = Community.create({
        'id': 'comm_id',
        'title': 'Title',
        'type': 'topic',
        'created_by': community_owner.id,
        'member_policy': 'open'
    }, id_=community_id)
    db.session.commit()
    CommunityIndexer().index_by_id(str(community.id))
    yield comid, community

