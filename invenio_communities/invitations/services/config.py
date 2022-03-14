# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitations Service Config."""

from invenio_records_resources.services import RecordServiceConfig
from invenio_records_resources.services.base.links import Link
from invenio_records_resources.services.records.config import \
    SearchOptions as SearchOptionsBase
from invenio_records_resources.services.records.links import pagination_links
from invenio_requests.customizations.base import RequestActions
from invenio_requests.services.requests import RequestItem, RequestList
from invenio_requests.services.requests.facets import status as status_facet


def _is_action_available(request, context):
    """Check if the given action is available on the request."""
    action = context.get("action")
    identity = context.get("identity")
    return RequestActions.can_execute(identity, request, action)


class InvitationLink(Link):
    """Shortcut for writing invitation links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template.

        This is only used for item-level 'links' serialization.
        """
        vars.update({"invitation_id": record.id})


class SearchOptions(SearchOptionsBase):
    """Search options."""

    facets = {
        'status': status_facet,
    }


class InvitationServiceConfig(RecordServiceConfig):
    """Invitation Service Config."""

    # TODO: Add permision
    # permission_policy_cls = PermissionPolicy

    # Search configuration
    search = SearchOptions

    result_item_cls = RequestItem
    result_list_cls = RequestList

    # Links
    links_item = {
        "self": InvitationLink(
            "{+api}/communities/{community_id}/invitations/{invitation_id}"
        ),
    }
    links_search = pagination_links(
        "{+api}/communities/{community_id}/invitations{?args*}"
    )
    action_link = InvitationLink(
        "{+api}/communities/{community_id}/invitations/{invitation_id}/actions/{action}",  # noqa
        when=_is_action_available
    )
