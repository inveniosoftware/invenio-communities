# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test components."""

from invenio_cache import current_cache
from invenio_access.permissions import system_identity
from invenio_communities.utils import identity_cache_key


def test_accept_invite_cache_clear(requests_service, invite_request_id, invite_user, db, es_clear):
    """Test that the community member cached entries are cleared."""
    current_cache.clear()
    cache_key = identity_cache_key(invite_user.identity)

    invite_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 0

    # cached entry should be cleared on accept_invite
    requests_service.execute_action(
        invite_user.identity, invite_request_id, 'accept')
    community_roles = current_cache.get(cache_key)
    assert community_roles == None
    invite_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 1
    
def test_member_delete_cache_clear(member_service, community, new_user, db, es_clear):
    """Test that the community member cached entries are cleared."""
    current_cache.clear()
    cache_key = identity_cache_key(new_user.identity)

    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 0

    # cached entry should be cleared on add
    add_data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, add_data)
    community_roles = current_cache.get(cache_key)
    assert community_roles == None
    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 1

    # cached entry should be cleared on delete
    delete_data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
    }
    member_service.delete(system_identity, community._record.id, delete_data)
    community_roles = current_cache.get(cache_key)
    assert community_roles == None
    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 0

def test_member_add_cache_clear(member_service, community, new_user, db, es_clear):
    """Test that the community member cached entries are cleared."""
    current_cache.clear()
    cache_key = identity_cache_key(new_user.identity)

    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 0

    # cached entry should be cleared on add
    add_data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, add_data)
    community_roles = current_cache.get(cache_key)
    assert community_roles == None
    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 1


def test_member_update_cache_clear(member_service, community, new_user, db, es_clear):
    """Test that the community member cached entries are cleared."""
    current_cache.clear()
    cache_key = identity_cache_key(new_user.identity)

    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 0

    # cached entry should be cleared on add
    add_data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.add(system_identity, community._record.id, add_data)
    community_roles = current_cache.get(cache_key)
    assert community_roles == None
    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 1

    update_data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": "reader",
    }
    member_service.update(system_identity, community._record.id, update_data)
    community_roles = current_cache.get(cache_key)
    assert community_roles == None
    new_user.refresh()
    community_roles = current_cache.get(cache_key)
    assert len(community_roles) == 1
