# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import pytest
from invenio_accounts.testutils import create_test_user
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
