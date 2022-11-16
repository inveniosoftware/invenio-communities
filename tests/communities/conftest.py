# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import pytest
from flask_security import login_user
from invenio_accounts.testutils import login_user_via_session
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.api import Affiliation


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture.
    Needed to set the files storage class list.
    """
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }

    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"

    return app_config


@pytest.fixture()
def affiliation(app, db, superuser_identity):
    """Affiliation vocabulary record."""
    aff = current_service_registry.get("affiliations").create(
        superuser_identity,
        {
            "name": "CERN",
            "id": "cern",
            "acronym": "CERN",
            "identifiers": [
                {
                    "scheme": "ror",
                    "identifier": "01ggx4157",
                },
                {
                    "scheme": "isni",
                    "identifier": "000000012156142X",
                },
            ],
        },
    )

    Affiliation.index.refresh()

    return aff


@pytest.fixture()
def client_with_login(client, users):
    """Log in a user to the client."""
    user = users[0]
    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)
    return client
