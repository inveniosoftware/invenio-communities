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

from invenio_records_resources.references.resolvers.records import \
    RecordPKProxy, RecordResolver

from ..generators import CommunityRoleNeed
from .records.api import Community


class CommunityPKProxy(RecordPKProxy):
    """Resolver proxy for a Record entity using the UUID."""

    def get_needs(self, ctx=None):
        """Return community member need."""
        ctx = ctx or {}
        roles = ctx.get(
            # TODO: replace with COMMUNITIES_ROLES
            'community_roles', ['owner', 'manager', 'curator', 'reader']
        )
        comid = str(self._parse_ref_dict_id(self._ref_dict))
        return [CommunityRoleNeed(comid, role) for role in roles]


class CommunityResolver(RecordResolver):
    """Community entity resolver.

    The entity resolver enables Invenio-Requests to understand communities as
    receiver and topic of a request.
    """

    type_id = 'community'
    """Type identifier for this resolver."""

    def __init__(self):
        """Initialize the default record resolver."""
        super().__init__(
            Community, type_key=self.type_id, proxy_cls=CommunityPKProxy)

    def _reference_entity(self, entity):
        """Create a reference dict for the given record."""
        return {self.type_key: str(entity.id)}
