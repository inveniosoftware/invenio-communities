# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test components."""

from copy import deepcopy
from datetime import datetime

import pytest
from invenio_access.permissions import system_identity
from invenio_oaiserver.models import OAISet

from invenio_communities.communities.services.components import OAISetComponent


def _retrieve_oaiset(service, community):
    comp = OAISetComponent(service)
    return OAISet.query.filter(
        OAISet.spec == comp._create_set_spec(community.get("slug"))
    ).first()


@pytest.fixture()
def comm(community_service, minimal_community, location):
    """Create minimal public community."""
    c = deepcopy(minimal_community)
    c["slug"] = "public-{slug}".format(
        slug=str(datetime.utcnow().timestamp()).replace(".", "-")
    )
    return community_service.create(data=c, identity=system_identity)


@pytest.fixture()
def comm_restricted(community_service, minimal_community, location):
    """Create minimal restricted community."""
    c = deepcopy(minimal_community)
    c["access"]["visibility"] = "restricted"
    c["slug"] = "restricted-{slug}".format(
        slug=str(datetime.utcnow().timestamp()).replace(".", "-")
    )
    return community_service.create(data=c, identity=system_identity)


def test_oai_set_create_community(community_service, comm, comm_restricted):
    """Set should only be created for public community."""
    oaiset = _retrieve_oaiset(service=community_service, community=comm.data)
    assert oaiset != None
    assert comm.data.get("id") in oaiset.search_pattern
    assert comm.data.get("slug") in oaiset.spec
    assert comm.data.get("metadata", {}).get("title") in oaiset.description
    assert comm.data.get("metadata", {}).get("title") in oaiset.name

    oaiset = _retrieve_oaiset(service=community_service, community=comm_restricted.data)
    assert oaiset == None


def test_oai_set_delete_community(community_service, comm, comm_restricted):
    """Set should be deleted for public community."""
    oaiset = _retrieve_oaiset(service=community_service, community=comm.data)
    assert oaiset != None

    community_service.delete(identity=system_identity, id_=comm.data.get("id"))
    oaiset = _retrieve_oaiset(service=community_service, community=comm.data)
    assert oaiset == None

    # nothing should happen for restricted communities
    community_service.delete(
        identity=system_identity, id_=comm_restricted.data.get("id")
    )


def test_oai_set_renamed(community_service, comm, comm_restricted):
    """Set should be deleted and new one created if public community is renamed."""
    new_data = deepcopy(comm.data)
    new_data["slug"] = "new-id-who-dis"
    r = community_service.rename(
        identity=system_identity, id_=comm.data.get("id"), data=new_data
    )

    # set with old id should not be there anymore
    old_oaiset = _retrieve_oaiset(service=community_service, community=comm.data)
    assert old_oaiset is None

    oaiset = _retrieve_oaiset(service=community_service, community=r.data)
    assert oaiset != None
    assert r.data.get("id") in oaiset.search_pattern
    assert r.data.get("slug") in oaiset.spec
    assert r.data.get("metadata", {}).get("title") in oaiset.description
    assert r.data.get("metadata", {}).get("title") in oaiset.name

    # nothing should happen for restricted communities
    new_data = deepcopy(comm_restricted.data)
    new_data["slug"] = "new-id-restricted-who-dis"
    r = community_service.rename(
        identity=system_identity, id_=comm_restricted.data.get("id"), data=new_data
    )
    old_oaiset = _retrieve_oaiset(service=community_service, community=r.data)
    assert old_oaiset == None


def test_oai_set_update(community_service, comm, comm_restricted):
    """Set should be updated accordingly."""
    new_data = deepcopy(comm.data)
    new_data["access"] = comm_restricted.data.get("access")
    community_service.update(identity=system_identity, id_=comm.id, data=new_data)
    # community not public anymore -> no set should be found
    oaiset = _retrieve_oaiset(service=community_service, community=comm.data)
    assert oaiset == None

    community_service.update(identity=system_identity, id_=comm.id, data=comm.data)
    # community public again -> set should be found
    oaiset = _retrieve_oaiset(service=community_service, community=comm.data)
    assert oaiset != None
    assert comm.id in oaiset.search_pattern
    assert comm.data.get("slug") in oaiset.spec
    assert comm.data.get("metadata", {}).get("title") in oaiset.description
    assert comm.data.get("metadata", {}).get("title") in oaiset.name

    new_data = deepcopy(comm.data)
    new_data["metadata"]["title"] = "new title"
    community_service.update(identity=system_identity, id_=comm.id, data=new_data)
    # community updated title -> set should update name/description
    oaiset = _retrieve_oaiset(service=community_service, community=comm.data)
    assert oaiset != None
    assert comm.id in oaiset.search_pattern
    assert comm.data.get("slug") in oaiset.spec
    assert new_data.get("metadata", {}).get("title") in oaiset.description
    assert new_data.get("metadata", {}).get("title") in oaiset.name
