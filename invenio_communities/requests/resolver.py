# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Entity resolver for the requests module.

Entity resolvers are considered part of the service-layer. The resolver
is registered in Invenio-Requests via the "invenio_requests.entity_resolvers"
entry point.
"""

from invenio_requests.resolvers.default import RecordResolver
from invenio_requests.resolvers.default.records import RecordPKProxy

from ..communities.records.api import Community


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
            Community, type_key=self.type_id, proxy_cls=RecordPKProxy)

    def _reference_entity(self, entity):
        """Create a reference dict for the given record."""
        return {self.type_key: str(entity.id)}
