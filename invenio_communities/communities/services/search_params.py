# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio Communities search params module."""
from invenio_records_resources.services.records.params import ParamInterpreter

from invenio_communities.communities.records.systemfields.deletion_status import (
    CommunityDeletionStatusEnum,
)


class StatusParam(ParamInterpreter):
    """Evaluates the 'status' parameter."""

    def apply(self, identity, search, params):
        """Evaluate the status parameter on the search."""
        value = params.pop("status", None)
        if value is not None and value in [
            x.value for x in CommunityDeletionStatusEnum
        ]:
            search = search.filter("term", **{"deletion_status": value})
        return search


class IncludeDeletedCommunitiesParam(ParamInterpreter):
    """Evaluates the include_deleted parameter."""

    def apply(self, identity, search, params):
        """Evaluate the include_deleted parameter on the search."""
        value = params.pop("include_deleted", None)
        # Filter prevents from displaying deleted records on main site search
        # deleted records should appear only in admins panel
        if value is None:
            search = search.filter(
                "term",
                **{"deletion_status": CommunityDeletionStatusEnum.PUBLISHED.value}
            )
        return search
