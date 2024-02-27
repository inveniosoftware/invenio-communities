# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test community service."""

import time
import uuid
from copy import deepcopy
from datetime import datetime, timedelta

import arrow
import pytest
from invenio_access.permissions import system_identity
from invenio_cache import current_cache
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow import ValidationError

from invenio_communities.communities.records.systemfields.deletion_status import (
    CommunityDeletionStatusEnum,
)
from invenio_communities.communities.services.service import get_cached_community_slug
from invenio_communities.errors import (
    CommunityFeaturedEntryDoesNotExistError,
    DeletionStatusError,
)
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


def test_search_featured(community_service, comm, db, search_clear):
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
    assert "links" in hits[0]
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


def test_reindex_featured_entries_task(community_service, comm, db, search_clear):
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


def test_cleanup_pre_search(db, search_clear):
    """Cleanup database and search for following tests.

    Tests before do not depend on a clean db or es. Cleanup is also an
    expensive task so te tests will run faster without them.
    """
    pass


def test_search_user(
    app,
    db,
    search_clear,
    location,
    anon_identity,
    community_service,
    community,
    members,
    new_user,
):
    current_cache.clear()
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
    search_clear,
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


#
# Deletion workflows
#


def test_community_deletion(community_service, users, comm):
    """Test simple community deletion of a community."""
    user = users["owner"].user
    community = comm

    assert community._obj.deletion_status == CommunityDeletionStatusEnum.PUBLISHED

    # delete the community
    tombstone_info = {"note": "no specific reason, tbh"}
    community = community_service.delete(system_identity, community.id, tombstone_info)
    tombstone = community._obj.tombstone

    # check if the tombstone information got added as expected
    assert community._obj.deletion_status == CommunityDeletionStatusEnum.DELETED
    assert tombstone.is_visible
    assert tombstone.removed_by == {"user": "system"}
    assert tombstone.removal_reason is None
    assert tombstone.note == tombstone_info["note"]
    assert isinstance(tombstone.citation_text, str)
    assert arrow.get(tombstone.removal_date).date() == datetime.utcnow().date()

    # mark the community for purge
    community = community_service.mark_community_for_purge(
        system_identity, community.id
    )
    assert community._obj.deletion_status == CommunityDeletionStatusEnum.MARKED
    assert community._obj.deletion_status.is_deleted
    assert community._obj.tombstone is not None

    # remove the mark again, we don't wanna purge it after all
    community = community_service.unmark_community_for_purge(
        system_identity, community.id
    )
    assert community._obj.deletion_status == CommunityDeletionStatusEnum.DELETED
    assert community._obj.deletion_status.is_deleted
    assert community._obj.tombstone is not None

    # restore the community, it wasn't so bad after all
    community = community_service.restore_community(system_identity, community.id)
    assert community._obj.deletion_status == CommunityDeletionStatusEnum.PUBLISHED
    assert not community._obj.deletion_status.is_deleted
    assert community._obj.tombstone is None


def test_invalid_community_deletion_workflows(community_service, comm):
    """Test the wrong order of deletion operations."""
    assert comm._obj.deletion_status == CommunityDeletionStatusEnum.PUBLISHED

    # we cannot restore a published community
    with pytest.raises(DeletionStatusError):
        community_service.restore_community(system_identity, comm.id)

    # we cannot mark a published community for purge
    with pytest.raises(DeletionStatusError):
        community_service.mark_community_for_purge(system_identity, comm.id)

    # we cannot unmark a published community
    with pytest.raises(DeletionStatusError):
        community_service.unmark_community_for_purge(system_identity, comm.id)

    comm = community_service.delete(system_identity, comm.id, {})
    assert comm._obj.deletion_status == CommunityDeletionStatusEnum.DELETED

    # we cannot unmark a deleted community
    with pytest.raises(DeletionStatusError):
        community_service.unmark_community_for_purge(system_identity, comm.id)

    comm = community_service.mark_community_for_purge(system_identity, comm.id)
    assert comm._obj.deletion_status == CommunityDeletionStatusEnum.MARKED

    # we cannot directly restore a community marked for purge
    with pytest.raises(DeletionStatusError):
        community_service.restore_community(system_identity, comm.id)


def test_get_cached_community_slug(community_service, comm, db, search_clear):
    """Test get_cached_community_slug."""
    c1 = community_service.create(
        identity=system_identity, data={**comm.data, "slug": "myslug"}
    )
    c2 = community_service.create(
        identity=system_identity, data={**comm.data, "slug": "myslug2"}
    )
    # reset
    get_cached_community_slug.cache_clear()
    # cache miss
    slug = get_cached_community_slug(c1.id, community_service.id)
    assert slug == "myslug"
    hits, misses = get_cached_community_slug.cache_info()
    assert (hits, misses) == (0, 1)
    # cache hit
    slug = get_cached_community_slug(c1.id, community_service.id)
    assert slug == "myslug"
    hits, misses = get_cached_community_slug.cache_info()
    assert (hits, misses) == (1, 1)
    # cache miss
    slug = get_cached_community_slug(c2.id, community_service.id)
    assert slug == "myslug2"
    hits, misses = get_cached_community_slug.cache_info()
    assert (hits, misses) == (1, 2)

    with pytest.raises(PIDDoesNotExistError):
        random_uuid = uuid.uuid4()
        get_cached_community_slug(random_uuid, community_service.id)


def test_theme_updates(
    app,
    db,
    search_clear,
    location,
    anon_identity,
    community_service,
    community,
    members,
    new_user,
):
    current_cache.clear()
    owner = members["owner"]

    theme_data = {
        "theme": {
            "style": {
                "primaryColor": "#004494",
                "tertiaryColor": "#e3eefd",
                "secondaryColor": "#FFD617",
                "primaryTextColor": "#FFFFFF",
                "tertiaryTextColor": "#1c5694",
                "secondaryTextColor": "#000000",
                "mainHeaderBackgroundColor": "#FFFFFF",
                "font": {"size": "16px", "family": "Arial, sans-serif", "weight": 600},
            },
            "brand": "horizon",
        }
    }

    # Update theme
    community_data = deepcopy(community.data)
    community_data.update(theme_data)

    # check if owner can update theme (early stage: it should not be possible)
    with pytest.raises(PermissionDeniedError):
        community_service.update(owner.identity, community.id, community_data)

    # only system can update the theme
    community_service.update(system_identity, community.id, community_data)
    community_item = community_service.read(system_identity, community.id)
    assert community_item.data["theme"]["brand"] == "horizon"

    # Update community data without passing theme should keep the stored theme
    community_data = deepcopy(community_item.data)
    community_data.pop("theme")

    community_service.update(system_identity, community.id, community_data)
    # Refresh index
    community_service.record_cls.index.refresh()

    # owner, anon, and system should be able to read the theme and see in search
    for idty in (owner.identity, anon_identity, system_identity):
        community_item = community_service.read(idty, community.id)
        assert community_item.data["theme"]["brand"] == "horizon"
        community_search = community_service.search(idty)
        assert next(community_search.hits)["theme"]["brand"] == "horizon"

    # Delete theme by setting to None
    community_data = deepcopy(community_item.data)
    community_data["theme"] = None

    # check if owner can delete theme (early stage: it should not be possible)
    with pytest.raises(PermissionDeniedError):
        community_service.update(owner.identity, community.id, community_data)

    # only system can delete the theme
    community_service.update(system_identity, community.id, community_data)
    community_item = community_service.read(system_identity, community.id)
    assert community_item.data.get("theme") is None

    # Set {theme: None} to a community that doesn't have any stored theme should not
    # store None value
    community_data = deepcopy(community_item.data)
    community_data["theme"] = None
    community_service.update(system_identity, community.id, community_data)
    community_item = community_service.read(system_identity, community.id)
    assert community_item.data.get("theme") is None
    assert "theme" not in community_item.data


def test_children_updates(
    app,
    db,
    search_clear,
    location,
    community_service,
    community,
    members,
):
    current_cache.clear()
    owner = members["owner"]

    # Update children
    community_data = deepcopy(community.data)
    community_data.update(dict(children=dict(allow=True)))

    # check if owner can update the children
    with pytest.raises(PermissionDeniedError):
        community_service.update(owner.identity, community.id, community_data)

    # only system can update the children
    community_service.update(system_identity, community.id, community_data)
    community_item = community_service.read(system_identity, community.id)
    assert community_item.data["children"]["allow"] == True

    # Update community data without passing children should keep the stored values
    community_data = deepcopy(community_item.data)
    community_data.pop("children")

    # Owner should be able to perfrom this operation since is not changing the children
    community_service.update(owner.identity, community.id, community_data)
    # Refresh index
    community_service.record_cls.index.refresh()


def test_parent_create(community_service, comm):
    parent = comm
    community_service.update(
        identity=system_identity,
        id_=str(parent.id),
        data={**parent.data, "children": {"allow": True}},
    )
    child = community_service.create(
        identity=system_identity,
        data={**comm.data, "slug": "child", "parent": {"id": str(parent.id)}},
    )
    assert str(child._obj.parent.id) == parent.id


def test_parent_update(community_service, comm):
    parent = comm
    community_service.update(
        identity=system_identity,
        id_=str(parent.id),
        data={**parent.data, "children": {"allow": True}},
    )
    child = community_service.create(
        identity=system_identity, data={**comm.data, "slug": "child1"}
    )

    child = community_service.update(
        identity=system_identity,
        id_=str(child.id),
        data={**child.data, "parent": {"id": str(parent.id)}},
    )
    assert str(child._obj.parent.id) == parent.id


def test_parent_remove(community_service, comm):
    parent = comm
    community_service.update(
        identity=system_identity,
        id_=str(parent.id),
        data={**parent.data, "children": {"allow": True}},
    )
    child = community_service.create(
        identity=system_identity,
        data={**comm.data, "slug": "child2", "parent": {"id": str(parent.id)}},
    )

    child = community_service.update(
        identity=system_identity, id_=str(child.id), data={**child.data, "parent": None}
    )
    assert child._obj.parent == None


def test_update_parent_community_not_exists(community_service, comm):
    child = comm

    with pytest.raises(ValidationError) as e:
        community_service.update(
            identity=system_identity,
            id_=str(child.id),
            data={**child.data, "parent": {"id": str(uuid.uuid4())}},
        )


def test_parent_update_parent_children_not_allowed(community_service, comm):
    parent = comm

    child = community_service.create(
        identity=system_identity, data={**comm.data, "slug": "child4"}
    )

    with pytest.raises(ValidationError) as e:
        community_service.update(
            identity=system_identity,
            id_=str(child.id),
            data={**child.data, "parent": {"id": str(parent.id)}},
        )


def test_parent_update_child_children_are_allowed(community_service, comm):
    parent = comm

    child = community_service.create(
        identity=system_identity, data={**comm.data, "slug": "child5"}
    )
    community_service.update(
        identity=system_identity,
        id_=str(parent.id),
        data={**parent.data, "children": {"allow": True}},
    )
    child = community_service.update(
        identity=system_identity,
        id_=str(child.id),
        data={**child.data, "children": {"allow": True}},
    )

    with pytest.raises(ValidationError) as e:
        community_service.update(
            identity=system_identity,
            id_=str(child.id),
            data={**child.data, "parent": {"id": str(parent.id)}},
        )


def test_bulk_update_parent(
    community_service, parent_community, comm, restricted_community
):
    """Test bulk add parent to children."""
    children = [comm.id, restricted_community.id]
    parent_community.children.allow = True
    parent_community.commit()
    community_service.bulk_update_parent(system_identity, children, parent_community.id)
    for c_id in children:
        c_comm = community_service.record_cls.pid.resolve(c_id)
        assert str(c_comm.parent.id) == str(parent_community.id)


def test_bulk_update_parent_overwrite(
    community_service, parent_community, comm, restricted_community
):
    """Test bulk update parent of communities that are already parented."""
    children = [comm.id]
    parent_community.children.allow = True
    parent_community.commit()
    community_service.bulk_update_parent(system_identity, children, parent_community.id)
    for c_id in children:
        c_comm = community_service.record_cls.pid.resolve(c_id)
        assert str(c_comm.parent.id) == str(parent_community.id)

    children = [comm.id, restricted_community.id]
    community_service.bulk_update_parent(system_identity, children, parent_community.id)
    for c_id in children:
        c_comm = community_service.record_cls.pid.resolve(c_id)
        assert str(c_comm.parent.id) == str(parent_community.id)
