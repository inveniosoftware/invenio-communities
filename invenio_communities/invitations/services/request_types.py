# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitation request types."""

from flask_babelex import lazy_gettext as _
from invenio_requests.customizations import RequestAction, RequestState, \
    BaseRequestType

from ...proxies import current_communities
from .schemas import MemberInvitationPayloadSchema

# Actions

class AcceptAction(RequestAction):
    """Accept action."""

    status_from = ['open']
    status_to = 'accepted'

    def can_execute(self, identity):
        """Check if the accept action can be executed."""
        # TODO
        return True

    def execute(self, identity, uow):
        """Accept entity into community."""
        member_data = {
            **self.request.receiver.reference_dict,
            **self.request.topic.reference_dict,
            "role": self.request["payload"]["role"]
        }

        current_communities.service.members.create(
            identity,
            data=member_data,
            uow=uow
        )

        super().execute(identity, uow)


# Request types

class CommunityMemberInvitation(BaseRequestType):
    """Community member invitation request type."""

    type_id = 'community-member-invitation'
    name = _('Community Member Invitation')
    available_statuses = {
        "open": RequestState.OPEN,
        "cancelled": RequestState.CLOSED,
        "declined": RequestState.CLOSED,
        "accepted": RequestState.CLOSED,
        "expired": RequestState.CLOSED,
    }
    default_status = "open"
    available_actions = {
        "accept": AcceptAction,
        # "cancel": CancelAction,
        # "decline": DeclineAction,
        # "expire": ExpireAction,
    }
    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["community"]
    allowed_receiver_ref_types = ["user"]
    allowed_topic_ref_types = ["community"]
    payload_schema = MemberInvitationPayloadSchema().fields
