# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2026 Northwestern University.
# Copyright (C) 2022-2025 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invitation request type."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services import ConditionalLink, EndpointLink
from invenio_requests.customizations import RequestType, actions

from invenio_communities.notifications.builders import (
    CommunityInvitationAcceptNotificationBuilder,
    CommunityInvitationCancelNotificationBuilder,
    CommunityInvitationDeclineNotificationBuilder,
    CommunityInvitationExpireNotificationBuilder,
)

from ...communities.services.service import get_cached_community_slug
from ...proxies import current_communities


def service():
    """Service."""
    return current_communities.service.members


#
# Request
#
def is_request_created_by_current_user(obj, vars):
    """Is created by current user.

    Because this is called in the context of a RequestType, the received obj
    can be a Request or RequestEvent, so better to trust the vars content.

    :param request: api.Request|api.RequestEvent
    :param vars: dict: context variables w/ keys:
        "permission_policy_cls" for api.Request
        "identity"
        "request"
        "request_type"
    """
    request = vars["request"]
    id_creator = str(request.created_by.reference_dict.get("user"))
    id_identity = str(vars["identity"].id)
    return id_identity == id_creator


def update_vars_for_user_dashboard_request_view(obj, vars):
    """Update vars.

    Because this is called in the context of a RequestType, the received obj
    can be a Request or RequestEvent so better to trust the vars content.

    :param obj: api.Request|api.RequestEvent
    :param vars: dict: context variables w/ keys:
        "permission_policy_cls" for api.Request
        "identity"
        "request"
        "request_type"
    """
    vars.update(request_pid_value=str(vars["request"].id))


def update_vars_for_community_dashboard_request_view(obj, vars):
    """Update vars.

    Because this is called in the context of a RequestType, the received obj
    can be a Request or RequestEvent so better to trust the vars content.

    :param obj: api.Request|api.RequestEvent
    :param vars: dict: context variables w/ keys:
        "permission_policy_cls" for api.Request
        "identity"
        "request"
        "request_type"
    """
    request = vars["request"]
    # The topic holds a CommunityPKProxy
    slug = get_cached_community_slug(request.topic.reference_dict["community"])
    vars.update(
        pid_value=slug,
        request_pid_value=request.id,
    )


#
# CommunityInvitation: actions and request type
#


#
# Actions
#
# All actions use `system_identity` and not the `identity` param, because
# the permission check happens at the request service (`execute_action`) level
# before reaching these components and therefore the check is not needed.
# These actions will assert the identity is `system identity`, which cannot
# be obtained as a user.
class AcceptAction(actions.AcceptAction):
    """Accept action."""

    def execute(self, identity, uow):
        """Execute action."""
        service().accept_member_request(system_identity, self.request.id, uow=uow)
        uow.register(
            NotificationOp(
                CommunityInvitationAcceptNotificationBuilder.build(self.request)
            )
        )
        super().execute(identity, uow)


class DeclineAction(actions.DeclineAction):
    """Delete action."""

    def execute(self, identity, uow):
        """Execute action."""
        service().close_member_request(system_identity, self.request.id, uow=uow)
        uow.register(
            NotificationOp(
                CommunityInvitationDeclineNotificationBuilder.build(self.request)
            )
        )
        super().execute(identity, uow)


class CancelAction(actions.CancelAction):
    """Cancel action."""

    def execute(self, identity, uow):
        """Execute action."""
        service().close_member_request(system_identity, self.request.id, uow=uow)
        uow.register(
            NotificationOp(
                CommunityInvitationCancelNotificationBuilder.build(self.request)
            )
        )
        super().execute(identity, uow)


class ExpireAction(actions.ExpireAction):
    """Expire action."""

    def execute(self, identity, uow):
        """Execute action."""
        service().close_member_request(system_identity, self.request.id, uow=uow)
        uow.register(
            NotificationOp(
                CommunityInvitationExpireNotificationBuilder.build(self.request)
            )
        )
        super().execute(identity, uow)


class CommunityInvitation(RequestType):
    """Community member invitation request type."""

    type_id = "community-invitation"
    name = _("Community invitation")

    create_action = "create"
    available_actions = {
        "create": actions.CreateAndSubmitAction,
        "delete": actions.DeleteAction,
        "accept": AcceptAction,
        "decline": DeclineAction,
        "cancel": CancelAction,
        "expire": ExpireAction,
    }

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["community"]
    allowed_receiver_ref_types = ["user"]
    allowed_topic_ref_types = ["community"]

    needs_context = {
        "community_roles": [
            "owner",
            "manager",
        ]
    }

    links_item = {
        "self_html": ConditionalLink(
            cond=is_request_created_by_current_user,
            if_=EndpointLink(
                "invenio_app_rdm_requests.user_dashboard_request_view",
                params=["request_pid_value"],
                vars=update_vars_for_user_dashboard_request_view,
            ),
            else_=EndpointLink(
                # TODO: Change to
                # invenio_app_rdm_requests.community_dashboard_invitation_view
                # when defined in invenio-app-rdm
                "invenio_app_rdm_requests.community_dashboard_request_view",
                params=["pid_value", "request_pid_value"],
                vars=update_vars_for_community_dashboard_request_view,
            ),
        )
    }


#
# MembershipRequestRequestType: actions and request type
#


class AcceptMembershipRequestAction(actions.AcceptAction):
    """Accept membership request action."""

    def execute(self, identity, uow):
        """Execute action."""
        service().accept_member_request(system_identity, self.request.id, uow=uow)
        # TODO: notifications for accept
        # uow.register(
        #     NotificationOp(
        #         (
        #             CommunityMembershipRequestAcceptNotificationBuilder.build(
        #                 self.request
        #             )
        #         )
        #     )
        # )
        super().execute(identity, uow)


class CancelMembershipRequestAction(actions.CancelAction):
    """Cancel membership request action."""

    def execute(self, identity, uow):
        """Execute action."""
        service().close_member_request(system_identity, self.request.id, uow=uow)
        # TODO: Investigate notifications
        super().execute(identity, uow)


class DeclineMembershipRequestAction(actions.DeclineAction):
    """Decline action."""

    def execute(self, identity, uow):
        """Execute action."""
        service().close_member_request(system_identity, self.request.id, uow=uow)
        # TODO: Notification for declining
        # uow.register(
        #     NotificationOp(
        #         (
        #             CommunityMembershipRequestDeclineNotificationBuilder
        #             .build(self.request)
        #         )
        #     )
        # )
        super().execute(identity, uow)


class MembershipRequestRequestType(RequestType):
    """Request type for membership requests."""

    type_id = "community-membership-request"
    name = _("Membership request")

    create_action = "create"
    available_actions = {
        "accept": AcceptMembershipRequestAction,
        "create": actions.CreateAndSubmitAction,
        "cancel": CancelMembershipRequestAction,
        "decline": DeclineMembershipRequestAction,
    }

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["user"]
    allowed_receiver_ref_types = ["community"]
    allowed_topic_ref_types = ["community"]

    links_item = {
        # This EndpointLink selection logic is better than existing logic for
        # other RequestTypes' self_html, bc it points to right place depending
        # on current user. But it may need further improvements down the road
        # to also depend on the state of the request.
        "self_html": ConditionalLink(
            cond=is_request_created_by_current_user,
            # if_ -> then_ : change when ConditionalLink is updated
            if_=EndpointLink(
                "invenio_app_rdm_requests.user_dashboard_request_view",
                params=["request_pid_value"],
                vars=update_vars_for_user_dashboard_request_view,
            ),
            else_=EndpointLink(
                "invenio_app_rdm_requests.community_dashboard_membership_request_view",
                params=["pid_value", "request_pid_value"],
                vars=update_vars_for_community_dashboard_request_view,
            ),
        )
    }
