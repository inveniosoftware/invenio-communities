# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitation request types."""

from flask_babelex import lazy_gettext as _
from invenio_requests.customizations import CancelAction, \
    CreateAndSubmitAction, DeclineAction, DeleteAction, ExpireAction, \
    RequestAction, RequestType

from ...proxies import current_communities
from .schemas import MemberInvitationPayloadSchema

# Actions

class AcceptAction(RequestAction):
    """Accept action."""

    status_from = ['submitted']
    status_to = 'accepted'

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


class CommunityMemberInvitation(RequestType):
    """Community member invitation request type."""

    type_id = 'community-invitation'
    name = _('Community invitation')
    create_action = 'create'
    available_actions = {
        "create": CreateAndSubmitAction,
        "delete": DeleteAction,
        "accept": AcceptAction,
        "cancel": CancelAction,
        "decline": DeclineAction,
        "expire": ExpireAction,
    }
    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["community"]
    allowed_receiver_ref_types = ["user"]
    allowed_topic_ref_types = ["community"]
    payload_schema = MemberInvitationPayloadSchema().fields
    needs_context = {
        "community_roles": ['owner', 'manager',]
    }
