# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test parent community."""

import pytest
from invenio_access.permissions import system_identity

from invenio_communities.communities.records.api import Community


def clean_child_comm(comm, db):
    """Remove parent from community."""
    comm.parent = None
    comm.commit()
    db.session.commit()


def test_set_parent_community_with_comm_obj(parent_community, child_community, db):
    child_community.parent = parent_community

    assert child_community.parent == parent_community

    child_community.commit()
    db.session.commit()

    comm = Community.get_record(str(child_community.id))
    assert comm.parent == parent_community

    clean_child_comm(comm, db)


def test_set_parent_community_with_comm_uuid(parent_community, child_community, db):
    child_community.parent = parent_community.id

    assert child_community.parent == parent_community

    child_community.commit()
    db.session.commit()

    comm = Community.get_record(str(child_community.id))
    assert comm.parent == parent_community

    clean_child_comm(comm, db)


def test_set_parent_community_with_comm_uuid_string(
    parent_community, child_community, db
):
    child_community.parent = str(parent_community.id)

    assert child_community.parent == parent_community

    child_community.commit()
    db.session.commit()
    comm = Community.get_record(str(child_community.id))
    assert comm.parent == parent_community

    clean_child_comm(comm, db)


def test_invalid_set_parent_community_with_comm_slug(parent_community, child_community):
    with pytest.raises(ValueError, match="Invalid parent community."):
        child_community.parent = parent_community.slug


def test_invalid_set_parent_community_with_random_object(child_community):
    with pytest.raises(ValueError, match="Invalid parent community."):
        child_community.parent = dict(test="test")


def test_parent_community_dereferencing(
    community_service, parent_community, child_community, db
):
    child_community.parent = parent_community

    assert child_community.parent == parent_community

    child_community.commit()
    db.session.commit()

    comm = Community.get_record(str(child_community.id))

    community_data = community_service.schema.dump(
        comm, context=dict(identity=system_identity)
    )
    parent_community_data = community_service.schema.dump(
        parent_community, context=dict(identity=system_identity)
    )
    assert comm.parent == parent_community

    # Make sure tha the parent community is dereferenced in the child community
    assert community_data["parent"] == parent_community_data

    clean_child_comm(comm, db)
