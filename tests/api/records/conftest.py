# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""
import pytest
from invenio_accounts.testutils import create_test_user, login_user_via_session
from invenio_app.factory import create_api


@pytest.fixture(scope='module')
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture(scope='module')
def basic_user(app):
    yield create_test_user('test@inveniosoftware.org')


@pytest.fixture(scope='module')
def users(app):
    yield [create_test_user('user{}@inveniosoftware.org'.format(i)) for i in range(3)]
