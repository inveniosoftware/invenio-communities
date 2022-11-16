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
from invenio_access.models import ActionRoles
from invenio_access.permissions import any_user as any_user_need
from invenio_access.permissions import superuser_access
from invenio_accounts.models import Role
from invenio_admin.permissions import action_admin_access
from invenio_app.factory import create_api
from invenio_records_resources.services.custom_fields import TextCF
from invenio_requests.proxies import current_events_service, current_requests_service
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from invenio_communities.communities.records.api import Community
from invenio_communities.members.records.api import Member
from invenio_communities.proxies import current_communities

pytest_plugins = ("celery.contrib.pytest",)


#
# Application
#
@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture."""
    app_config[
        "RECORDS_REFRESOLVER_CLS"
    ] = "invenio_records.resolver.InvenioRefResolver"
    app_config[
        "RECORDS_REFRESOLVER_STORE"
    ] = "invenio_jsonschemas.proxies.current_refresolver_store"
    # Variable not used. We set it to silent warnings
    app_config["JSONSCHEMAS_HOST"] = "not-used"

    # Custom fields
    app_config["COMMUNITIES_CUSTOM_FIELDS"] = [
        TextCF(name="mycommunityfield", use_as_filter=True),
    ]

    # Define files storage class list
    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
        "F": "Fetch",
        "R": "Remote",
    }
    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"

    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api


@pytest.fixture()
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
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


@pytest.fixture(scope="module")
def vocabularies_service(app):
    """Vocabularies service."""
    return vocabulary_service


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
    """Users."""
    users = {}
    for r in ["owner", "manager", "curator", "reader"]:
        u = UserFixture(
            email=f"{r}@{r}.org",
            password=r,
        )
        u.create(app, database)
        users[r] = u
    # when using `database` fixture (and not `db`), commit the creation of the
    # user because its implementation uses a nested session instead
    database.session.commit()
    return users


@pytest.fixture(scope="module")
def group(database):
    """Group."""
    r = Role(name="it-dep")
    database.session.add(r)
    database.session.commit()
    return r


@pytest.fixture(scope="module")
def owner(users):
    """Community owner user."""
    return users["owner"]


@pytest.fixture(scope="module")
def any_user(UserFixture, app, database):
    """A user without privileges or memberships."""
    u = UserFixture(
        email=f"anyuser@anyuser.org",
        password="anyuser",
    )
    u.create(app, database)
    # when using `database` fixture (and not `db`), commit the creation of the
    # user because its implementation uses a nested session instead
    database.session.commit()
    u.identity  # compute identity
    return u


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(u.user, "admin-access")

    datastore.add_role_to_user(u.user, role)
    datastore.commit()
    return u


@pytest.fixture()
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture()
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="admin-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=action_admin_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture(scope="module")
def new_user(UserFixture, app, database):
    """A new user."""
    u = UserFixture(
        email=f"newuser@newuser.org",
        password="newuser",
        user_profile={
            "full_name": "New User",
            "affiliations": "CERN",
        },
        preferences={
            "visibility": "public",
            "email_visibility": "restricted",
        },
        active=True,
        confirmed=True,
    )
    u.create(app, database)
    # when using `database` fixture (and not `db`), commit the creation of the
    # user because its implementation uses a nested session instead
    database.session.commit()
    return u


#
# Communities
#
@pytest.fixture(scope="module")
def minimal_community():
    """Minimal community metadata."""
    return {
        "access": {
            "visibility": "public",
            "record_policy": "open",
        },
        "slug": "public",
        "metadata": {
            "title": "My Community",
        },
    }


@pytest.fixture(scope="module")
def full_community():
    """Full community data as dict coming from the external world."""
    return {
        "access": {
            "visibility": "public",
            "member_policy": "open",
            "record_policy": "open",
        },
        "slug": "my_community_id",
        "metadata": {
            "title": "My Community",
            "description": "This is an example Community.",
            "type": {"id": "event"},
            "curation_policy": "This is the kind of records we accept.",
            "page": "Information for my community.",
            "website": "https://inveniosoftware.org/",
            "organizations": [
                {
                    "name": "My Org",
                }
            ],
        },
    }


@pytest.fixture(scope="module")
def community(community_service, owner, minimal_community, location):
    """A community."""
    c = community_service.create(owner.identity, minimal_community)
    Community.index.refresh()
    owner.refresh()
    return c


@pytest.fixture(scope="module")
def restricted_community(community_service, owner, minimal_community, location):
    """A restricted community."""
    data = deepcopy(minimal_community)
    data["access"]["visibility"] = "restricted"
    data["slug"] = "restricted"
    c = community_service.create(owner.identity, data)
    owner.refresh()
    return c


@pytest.fixture(scope="function")
def fake_communities(
    community_service,
    owner,
    minimal_community,
    location,
    db,
    community_type_record,
    community_types,
):
    """Fake Communities."""
    data = deepcopy(minimal_community)
    """Multiple community created and posted to test search functionality."""
    N = 4
    for (type_, ind) in itertools.product(community_types, list(range(N))):
        data["slug"] = f'comm_{type_["id"]}_{ind}'
        data["metadata"]["type"] = {"id": type_["id"]}
        c = community_service.create(owner.identity, data)
    Community.index.refresh()

    # Return ids of first and last created communities
    return "comm_organization_0", "comm_project_3", N, N * len(community_types)


#
# Community types
#
@pytest.fixture(scope="module")
def community_types():
    """Community types."""
    return [
        {"id": "organization", "title": {"en": "Organization"}},
        {"id": "event", "title": {"en": "Event"}},
        {"id": "topic", "title": {"en": "Topic"}},
        {"id": "project", "title": {"en": "Project"}},
    ]


@pytest.fixture()
def community_type_type(superuser_identity, vocabularies_service):
    """Creates and retrieves a language vocabulary type."""
    v = vocabularies_service.create_type(superuser_identity, "communitytypes", "comtyp")
    return v


@pytest.fixture(scope="module")
def community_types_data(community_types):
    """Example data."""
    return [
        {
            **ct,
            "type": "communitytypes",
        }
        for ct in community_types
    ]


@pytest.fixture()
def community_type_record(
    superuser_identity, community_types_data, community_type_type, vocabularies_service
):
    """Creates a d retrieves community type records."""
    records_list = []
    for community_type_data in community_types_data:
        record = vocabularies_service.create(
            identity=superuser_identity, data=community_type_data
        )
        records_list.append(record)

    Vocabulary.index.refresh()  # Refresh the index
    return records_list


@pytest.fixture(scope="function")
def members(member_service, community, users, db):
    """Members."""
    for name, user in users.items():
        if name == "owner":
            continue
        m = Member.create(
            {},
            community_id=community._record.id,
            user_id=user.id,
            role=name,
            visible=False,
            active=True,
        )
        member_service.indexer.index(m)
        Member.index.refresh()
    db.session.commit()
    return users


@pytest.fixture(scope="module")
def cli_runner(base_app):
    """Create a CLI runner for testing a CLI command."""

    def cli_invoke(command, *args, input=None):
        return base_app.test_cli_runner().invoke(command, args, input=input)

    return cli_invoke
