# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community service."""

import time
from copy import deepcopy
from datetime import datetime, timedelta

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from invenio_communities.errors import CommunityFeaturedEntryDoesNotExistError
from invenio_communities.fixtures.tasks import reindex_featured_entries


@pytest.fixture()
def comm(community_service, minimal_community, location):
    """Create minimal public community."""
    c = deepcopy(minimal_community)
    c["slug"] = "{slug}".format(
        slug=str(datetime.utcnow().timestamp()).replace(".", "-")
    )
    return community_service.create(data=c, identity=system_identity)


@pytest.fixture()
def comm_restricted(community_service, minimal_community, location):
    """Create minimal restricted community."""
    c = deepcopy(minimal_community)
    c["slug"] = "{slug}".format(
        slug=str(datetime.utcnow().timestamp()).replace(".", "-")
    )
    c["access"]["visibility"] = "restricted"
    return community_service.create(data=c, identity=system_identity)


def test_search_featured(community_service, comm, db, es_clear):
    """Test that featured entries are indexed and returned correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    # no featured entries -> no featured communities
    featured_comms = community_service.featured_search(
        identity=system_identity
    ).to_dict()
    assert len(featured_comms["hits"]["hits"]) == featured_comms["hits"]["total"] == 0

    # added one featured entry in the past. community should now be returned
    community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=data
    ).to_dict()
    featured_comms = community_service.featured_search(
        identity=system_identity
    ).to_dict()
    hits = featured_comms["hits"]["hits"]
    assert len(hits) == featured_comms["hits"]["total"] == 1
    assert hits[0]["id"] == comm.data["id"]
    # featured entries should not show up in search results
    assert "featured" not in hits[0]

    # new community with only future entry should not show up in search
    c2 = community_service.create(
        identity=system_identity, data={**comm.data, "slug": "c2-id"}
    )
    community_service.featured_create(
        identity=system_identity, community_id=c2.data["id"], data=future_data
    ).to_dict()
    featured_comms = community_service.featured_search(
        identity=system_identity
    ).to_dict()
    hits = featured_comms["hits"]["hits"]
    assert len(hits) == featured_comms["hits"]["total"] == 1
    assert hits[0]["id"] == comm.data["id"]

    # adding past featured entry to new community. first community should show up first
    data["start_date"] = (datetime.utcnow() - timedelta(days=1)).isoformat()
    community_service.featured_create(
        identity=system_identity, community_id=c2.data["id"], data=data
    ).to_dict()
    featured_comms = community_service.featured_search(
        identity=system_identity
    ).to_dict()
    hits = featured_comms["hits"]["hits"]
    assert len(hits) == featured_comms["hits"]["total"] == 2
    assert hits[0]["id"] == comm.data["id"]
    assert hits[1]["id"] == c2.data["id"]

    # adding more current past featured entry to new community. new community should show up first
    data["start_date"] = datetime.utcnow().isoformat()
    community_service.featured_create(
        identity=system_identity, community_id=c2.data["id"], data=data
    ).to_dict()
    featured_comms = community_service.featured_search(
        identity=system_identity
    ).to_dict()
    hits = featured_comms["hits"]["hits"]
    assert len(hits) == featured_comms["hits"]["total"] == 2
    assert hits[0]["id"] == c2.data["id"]
    assert hits[1]["id"] == comm.data["id"]


def test_reindex_featured_entries_task(community_service, comm, db, es_clear):
    """Test that reindexing task works."""
    tomorrow = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }
    c2 = community_service.create(
        identity=system_identity, data={**comm.data, "slug": "c2-id"}
    )
    community_service.featured_create(
        identity=system_identity, community_id=c2.data["id"], data=tomorrow
    ).to_dict()

    near_future_difference = 2
    near_future = {
        "start_date": (
            datetime.utcnow() + timedelta(seconds=near_future_difference)
        ).isoformat(),
    }
    community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=near_future
    ).to_dict()
    featured_comms = community_service.featured_search(
        identity=system_identity
    ).to_dict()
    hits = featured_comms["hits"]["hits"]
    assert len(hits) == featured_comms["hits"]["total"] == 0

    time.sleep(near_future_difference)
    reindex_featured_entries()

    # only one community should be reindexed and returned
    featured_comms = community_service.featured_search(
        identity=system_identity
    ).to_dict()
    hits = featured_comms["hits"]["hits"]
    assert len(hits) == featured_comms["hits"]["total"] == 1
    assert hits[0]["id"] == comm.data["id"]


def test_create_featured(community_service, comm, comm_restricted):
    """Test that a featured entry can be created."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }

    f = community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=data
    ).to_dict()
    assert f["start_date"] == data["start_date"]
    assert f["id"]

    # can not create entry for a non-public community
    with pytest.raises(ValidationError):
        community_service.featured_create(
            identity=system_identity, community_id=comm_restricted.data["id"], data=data
        )

    # can not create entry with invalid data
    with pytest.raises(ValidationError):
        community_service.featured_create(
            identity=system_identity, community_id=comm.data["id"], data={}
        )


def test_get_featured(community_service, comm):
    """Test that featured entries are indexed and returned correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=data
    )
    community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=future_data
    )
    featured = community_service.featured_list(
        identity=system_identity, community_id=comm.data["id"]
    ).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 2
    assert featured["hits"]["hits"][0]["start_date"] == data["start_date"]
    assert featured["hits"]["hits"][1]["start_date"] == future_data["start_date"]


def test_delete_featured(community_service, comm):
    """Test that featured entries are deleted correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    past_entry = community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=data
    ).to_dict()
    community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=future_data
    ).to_dict()
    featured = community_service.featured_list(
        identity=system_identity, community_id=comm.data["id"]
    ).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 2

    community_service.featured_delete(
        identity=system_identity,
        community_id=comm.data["id"],
        featured_id=past_entry["id"],
    )
    featured = community_service.featured_list(
        identity=system_identity, community_id=comm.data["id"]
    ).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 1
    assert featured["hits"]["hits"][0]["start_date"] == future_data["start_date"]

    # Error when trying to delete entry which is already deleted
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_delete(
            identity=system_identity,
            community_id=comm.data["id"],
            featured_id=past_entry["id"],
        )

    # Error when trying to delete entry which does not exist
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_delete(
            identity=system_identity, community_id=comm.data["id"], featured_id=9999
        )


def test_update_featured(community_service, comm):
    """Test that featured entries are indexed and returned correctly."""
    data = {
        "start_date": datetime.utcnow().isoformat(),
    }
    future_data = {
        "start_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }

    past_entry = community_service.featured_create(
        identity=system_identity, community_id=comm.data["id"], data=data
    ).to_dict()
    updated_entry = community_service.featured_update(
        identity=system_identity,
        community_id=comm.data["id"],
        featured_id=past_entry["id"],
        data=future_data,
    ).to_dict()
    assert updated_entry["id"] == past_entry["id"]
    assert updated_entry["start_date"] != past_entry["start_date"]

    featured = community_service.featured_list(
        identity=system_identity, community_id=comm.data["id"]
    ).to_dict()
    assert len(featured["hits"]["hits"]) == featured["hits"]["total"] == 1
    assert featured["hits"]["hits"][0]["start_date"] == future_data["start_date"]

    # Error when trying to update entry which does not exist
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_update(
            identity=system_identity,
            community_id=comm.data["id"],
            featured_id=9999,
            data=future_data,
        ).to_dict()

    # Error when trying to update entry with invalid data
    with pytest.raises(ValidationError):
        x = community_service.featured_update(
            identity=system_identity,
            community_id=comm.data["id"],
            featured_id=past_entry["id"],
            data={},
        ).to_dict()
        print(x)

    community_service.featured_delete(
        identity=system_identity,
        community_id=comm.data["id"],
        featured_id=past_entry["id"],
    )

    # Error when trying to update entry which is already deleted
    with pytest.raises(CommunityFeaturedEntryDoesNotExistError):
        community_service.featured_update(
            identity=system_identity,
            community_id=comm.data["id"],
            featured_id=past_entry["id"],
            data=future_data,
        ).to_dict()


def test_cleanup_pre_search(db, es_clear):
    """Cleanup database and elasticsearch for following tests.

    Tests before do not depend on a clean db or es. Cleanup is also an
    expensive task so te tests will run faster without them.
    """
    pass


def test_search_user(
    app,
    db,
    es_clear,
    location,
    anon_identity,
    community_service,
    community,
    members,
    new_user,
):
    owner = members["owner"]
    reader = members["reader"]

    # Community members see them
    hits = community_service.search_user_communities(identity=owner.identity).to_dict()[
        "hits"
    ]["hits"]

    assert 1 == len(hits)
    assert {h["id"] for h in hits} & {community["id"]}

    hits = community_service.search_user_communities(
        identity=reader.identity
    ).to_dict()["hits"]["hits"]
    assert 1 == len(hits)
    assert {h["id"] for h in hits} & {community["id"]}

    # Non-community members don't see them
    hits = community_service.search_user_communities(
        identity=new_user.identity
    ).to_dict()["hits"]["hits"]
    assert 0 == len(hits)

    with pytest.raises(PermissionDeniedError):
        community_service.search_user_communities(identity=anon_identity)


def test_search_community_requests(
    app,
    db,
    es_clear,
    location,
    anon_identity,
    community_service,
    community,
    members,
    new_user,
):
    """Test who cannot see community requests.

    Community managers should be the one able to see the community requests
    This test should happen in invenio-rdm-records where the review service is defined.
    """
    reader = members["reader"]

    # Community members don't see them
    with pytest.raises(PermissionDeniedError):
        community_service.search_community_requests(
            identity=reader.identity, community_id=community.id
        )

    # Non-community members don't see them
    with pytest.raises(PermissionDeniedError):
        community_service.search_community_requests(
            identity=new_user.identity, community_id=community.id
        )

    # Anonymous users don't see them
    with pytest.raises(PermissionDeniedError):
        community_service.search_community_requests(
            identity=anon_identity, community_id=community.id
        )
