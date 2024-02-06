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

from invenio_communities.communities.records.api import Community


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


@pytest.fixture(scope="module")
def parent_community(community_service, owner, minimal_community, location):
    """A community."""
    minimal_community["slug"] = "parent"
    minimal_community["title"] = "Parent Community"
    c = community_service.create(owner.identity, minimal_community)
    Community.index.refresh()
    owner.refresh()
    return c._record


@pytest.fixture(scope="module")
def child_community(community_service, owner, minimal_community, location):
    """A community."""
    minimal_community["slug"] = "child"
    minimal_community["title"] = "Child Community"
    c = community_service.create(owner.identity, minimal_community)
    Community.index.refresh()
    owner.refresh()
    return c._record
