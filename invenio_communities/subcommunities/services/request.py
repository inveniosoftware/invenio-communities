# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Subcommunity request implementation."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_requests.customizations import RequestType, actions

import invenio_communities.notifications.builders as notifications
from invenio_communities.proxies import current_communities


class AcceptSubcommunity(actions.AcceptAction):
    """Represents an accept action used to accept a subcommunity."""

    def execute(self, identity, uow):
        """Execute approve action."""
        to_be_moved = self.request.topic.resolve().id
        move_to = self.request.receiver.resolve().id
        current_communities.service.bulk_update_parent(
            system_identity, [to_be_moved], parent_id=move_to, uow=uow
        )
        uow.register(
            NotificationOp(
                notifications.SubCommunityAccept.build(
                    identity=identity, request=self.request
                )
            )
        )
        super().execute(identity, uow)


class DeclineSubcommunity(actions.DeclineAction):
    """Represents a decline action used to decline a subcommunity."""

    def execute(self, identity, uow):
        """Execute decline action."""
        # We override just to send a notification
        uow.register(
            NotificationOp(
                notifications.SubCommunityDecline.build(
                    identity=identity, request=self.request
                )
            )
        )
        super().execute(identity, uow)


class SubCommunityRequest(RequestType):
    """Request to add a subcommunity to a community."""

    type_id = "subcommunity"
    name = _("Subcommunity Request")

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["community"]
    allowed_receiver_ref_types = ["community"]
    allowed_topic_ref_types = ["community"]

    available_actions = {
        "delete": actions.DeleteAction,
        "create": actions.CreateAndSubmitAction,
        "cancel": actions.CancelAction,
        # Custom implemented actions
        "accept": AcceptSubcommunity,
        "decline": DeclineSubcommunity,
    }

    needs_context = {
        "community_roles": [
            "owner",
            "manager",
        ]
    }


def subcommunity_request_type(app):
    """Return the subcommunity request type.

    Since it can be overridden by the application, this function should be used
    as the entry point for the request type.

    It must return a class that inherits from `RequestType`.
    """
    if not app:
        return
    return app.config.get("COMMUNITIES_SUB_REQUEST_CLS", SubCommunityRequest)
