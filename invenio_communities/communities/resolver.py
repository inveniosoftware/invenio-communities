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

from .records.api import Community
from .services.permissions import CommunityNeed


class CommunityPKProxy(RecordPKProxy):
    """Resolver proxy for a Record entity using the UUID."""

    def get_need(self):
        """Return the user need of the community's owner."""
        # TODO this may become difficult once there's multiple levels
        #      of membership (owner, manager, curator, ...)
        #      -> which needs should be generated? None, and let the
        #         user create the set of required needs from the
        #         resolved entity? or keep the 'owner' need?
        comid = str(self._parse_ref_dict_id(self._ref_dict))
        return CommunityNeed(comid)


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
