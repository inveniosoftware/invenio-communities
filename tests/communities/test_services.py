# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community member service."""

from datetime import datetime, timedelta
import arrow
import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound
from invenio_communities.errors import CommunityFeaturedEntryDoesNotExistError


from invenio_communities.members.errors import AlreadyMemberError, \
    InvalidMemberError
from invenio_communities.members.records.api import ArchivedInvitation, Member


@pytest.fixture()
def comm(community_service, minimal_community, location):
    """Create minimal public community."""
    return community_service.create(data=minimal_community, identity=system_identity)

@pytest.fixture()
def comm_restricted(community_service, minimal_community, location):
    """Create minimal restricted community."""
    minimal_community["access"]["visibility"] = "restricted"
    minimal_community["id"] = "restricted"
    return community_service.create(data=minimal_community, identity=system_identity)


def test_create_featured(community_service, comm, comm_restricted, db):
    """Test that a featured entry can be created."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }

    f = community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data=data).to_dict()
    assert f["start_date"] == data["start_date"]
    assert f["id"]

    # can not create entry for a non-public community
    with pytest.raises(ValidationError):
        community_service.featured_create(identity=system_identity, community_id=comm_restricted.data["id"], data=data)

    # can not create entry with invalid data
    with pytest.raises(ValidationError):
        community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data={})

def test_get_featured(community_service, comm, db):
    """Test that featured entries are indexed and returned correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data=data)
    community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data=future_data)
    featured = community_service.featured_list(identity=system_identity, community_id=comm.data["id"]).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 2
    assert featured["hits"]["hits"][0]["start_date"] == data["start_date"]
    assert featured["hits"]["hits"][1]["start_date"] == future_data["start_date"]

def test_delete_featured(community_service, comm, db):
    """Test that featured entries are indexed and returned correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    past_entry = community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data=data).to_dict()
    community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data=future_data).to_dict()
    featured = community_service.featured_list(identity=system_identity, community_id=comm.data["id"]).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 2

    community_service.featured_delete(identity=system_identity, community_id=comm.data["id"], featured_id=past_entry["id"])
    featured = community_service.featured_list(identity=system_identity, community_id=comm.data["id"]).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 1
    assert featured["hits"]["hits"][0]["start_date"] == future_data["start_date"]

    # Error when trying to delete entry which is already deleted
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_delete(identity=system_identity, community_id=comm.data["id"], featured_id=past_entry["id"])

    # Error when trying to delete entry which does not exist
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_delete(identity=system_identity, community_id=comm.data["id"], featured_id=9999)

def test_update_featured(community_service, comm, db):
    """Test that featured entries are indexed and returned correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    past_entry = community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data=data).to_dict()
    updated_entry = community_service.featured_update(identity=system_identity, community_id=comm.data["id"], featured_id=past_entry["id"], data=future_data).to_dict()
    assert updated_entry["id"] == past_entry["id"]
    assert updated_entry["start_date"] != past_entry["start_date"]

    featured = community_service.featured_list(identity=system_identity, community_id=comm.data["id"]).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 1
    assert featured["hits"]["hits"][0]["start_date"] == future_data["start_date"]

    # Error when trying to update entry which does not exist
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_update(identity=system_identity, community_id=comm.data["id"], featured_id=9999, data=future_data).to_dict()
    
    # Error when trying to update entry with invalid data 
    with pytest.raises(ValidationError):
        x = community_service.featured_update(identity=system_identity, community_id=comm.data["id"], featured_id=past_entry["id"], data={}).to_dict()
        print(x)

    community_service.featured_delete(identity=system_identity, community_id=comm.data["id"], featured_id=past_entry["id"])

    # Error when trying to update entry which is already deleted
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_update(identity=system_identity, community_id=comm.data["id"], featured_id=past_entry["id"], data=future_data).to_dict()

def test_update_featured_search(community_service, comm, db):
    """Test that featured entries are indexed and returned correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    past_entry = community_service.featured_create(identity=system_identity, community_id=comm.data["id"], data=data).to_dict()
    featured_comms = community_service.featured_search(identity=system_identity).to_dict()
    assert len(featured_comms["hits"]["hits"]) == featured_comms["hits"]["total"] == 1
    assert featured_comms["hits"]["hits"] == None
