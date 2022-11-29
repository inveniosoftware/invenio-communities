# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Entity resolver for the requests module.

Entity resolvers are considered part of the service-layer. The resolver
is registered in Invenio-Requests via the "invenio_requests.entity_resolvers"
entry point.
"""

from types import SimpleNamespace

from invenio_records_resources.references.resolvers.records import (
    RecordPKProxy,
    RecordResolver,
)

from ..generators import CommunityRoleNeed
from ..proxies import current_communities, current_roles
from .records.api import Community
from .services.config import CommunityServiceConfig


def pick_fields(identity, community_dict):
    """Pick fields to return when expanding the community obj."""
    fake_community_obj = SimpleNamespace(
        id=community_dict["id"],
        slug=community_dict["slug"],
    )
    logo = current_communities.service.links_item_tpl.expand(
        identity, fake_community_obj
    )["logo"]
    metadata = community_dict["metadata"]
    access = community_dict["access"]
    return {
        "id": community_dict["id"],
        "slug": community_dict["slug"],
        "links": {"logo": logo},
        "metadata": {
            "title": metadata["title"],
            "description": metadata.get("description"),
            "type": metadata.get("type"),
        },
        "access": {"visibility": access["visibility"]},
    }


class CommunityPKProxy(RecordPKProxy):
    """Resolver proxy for a Record entity using the UUID."""

    def get_needs(self, ctx=None):
        """Return community member need."""
        ctx = ctx or {}
        roles = ctx.get("community_roles", [role.name for role in current_roles])
        comid = str(self._parse_ref_dict_id())
        return [CommunityRoleNeed(comid, role) for role in roles]

    def pick_resolved_fields(self, identity, resolved_dict):
        """Select which fields to return when resolving the reference."""
        return pick_fields(identity, resolved_dict)


class CommunityResolver(RecordResolver):
    """Community entity resolver.

    The entity resolver enables Invenio-Requests to understand communities as
    receiver and topic of a request.
    """

    type_id = "community"
    """Type identifier for this resolver."""

    def __init__(self):
        """Initialize the default record resolver."""
        super().__init__(
            Community,
            CommunityServiceConfig.service_id,
            type_key=self.type_id,
            proxy_cls=CommunityPKProxy,
        )

    def _reference_entity(self, entity):
        """Create a reference dict for the given record."""
        return {self.type_key: str(entity.id)}
