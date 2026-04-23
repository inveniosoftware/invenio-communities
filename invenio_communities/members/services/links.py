# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Northwestern University.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Members Service links."""

from collections import namedtuple

from invenio_records_resources.services.base.links import (
    EndpointLink,
)
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.services.links import RequestTypeDependentEndpointLink

from .request import CommunityInvitation, MembershipRequestRequestType


def _can_execute(request_action, request_status):
    """Reprise logic of `RequestActions.can_execute` without actual api.Request."""
    if request_action.status_from is None:
        return request_status is None
    else:
        return request_status in request_action.status_from


def _is_context_action_possible(member, context):
    """Check if the action (in context) for the member's request is possible.

    Does equivalent of `RequestActions.can_execute` (equivalent of permission check is
    done in `MemberRequestActionsEndpointLinks._available_action_ids_for_member`).
    This is more "in case" as the status should always be 'submitted' at this point
    barring manual intervention.

    Assumptions at this point:
    - member has a request
    - context has action

    :param member: api.Member (where Member represents an invitation or mshp request)
    :param context: dict
    """
    action_id = context["action"]
    request_type_id = member["request"].get("type", "community-invitation")
    request_type = current_request_type_registry.lookup(request_type_id)
    request_action = request_type.available_actions[action_id]
    request_status = member["request"]["status"]
    return _can_execute(request_action, request_status)


class MemberRequestActionEndpointLink(EndpointLink):
    """EndpointLink for the action of a request."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            "requests.execute_action",
            params=["id", "action"],
            when=_is_context_action_possible,
        )

    @staticmethod
    def vars(record, vars):
        """Update vars with values used to expand the link."""
        vars.update({"id": record.request_id})


class MemberRequestActionsEndpointLinks:
    """Renders action links related to the request of the member.

    This is 'EndpointLink-input-interface' compliant, but renders a dict of
    links. That's why we don't inherit from it directly.
    """

    def __init__(self):
        """Constructor."""
        self._endpoint_link = MemberRequestActionEndpointLink()

    def _available_action_ids_for_member(self, obj, context):
        """Available request action ids for member.

        Actions are based on the request connected to the member.
        Action ids returned are strings that can be used to retrieve associated
        RequestAction object.

        Because we don't have a full request object
        (notably missing created_by, topic, receiver...), we can't rely on a
        RequestPermissionPolicy for permission of each action. However, actions links
        are only shown for invitations and membership requests and only specific ones
        for each. Knowing there is also no MemberService.read
        (only search/search_invitations/search_membership_requests contexts), we
        can embed the logic to determine the available actions here.

        :param obj: api.Member
        :param context: dict of context variables
        :return: list<str>
        """
        # No request actions for active member or members without request
        # (members that were added directly)
        if obj.active or not obj.get("request"):
            return []

        # Not all requests have a type since Member was created before we started
        # storing the request type. In the case of a Member missing a type, at this
        # point we know the Member is inactive, but has a request, so the request must
        # be an invitation (the assumption existing before storing request type).
        request_type_id = obj["request"].get("type") or "community-invitation"

        # Get its actions. This is where we shortcut the normal request permission
        # policy check - which is legitimate.
        if request_type_id == CommunityInvitation.type_id:
            return ["cancel"]
        elif request_type_id == MembershipRequestRequestType.type_id:
            return ["accept", "decline"]
        else:
            return []

    def _action_injected_context(self, context, action_id):
        """Return a context with action_id injected in it under "action" key.

        This has to be done because the endpoint route expects "action" as a parameter.
        We use action_id until then because it is more precise and distinct from
        a RequestAction object.
        """
        ctx = context.copy()
        ctx["action"] = action_id
        return ctx

    def should_render(self, obj, context):
        """Only render if any action would render.

        :param obj: api.Member
        :param context: dict of context variables
        """
        return any(
            self._endpoint_link.should_render(
                obj, self._action_injected_context(context, action_id)
            )
            for action_id in self._available_action_ids_for_member(obj, context)
        )

    def expand(self, obj, context):
        """Expand the endpoints.

        :param obj: api.Member
        :param context: dict of context data
        """
        links = {}

        for action in self._available_action_ids_for_member(obj, context):
            ctx = self._action_injected_context(context, action)
            if self._endpoint_link.should_render(obj, ctx):
                links[action] = self._endpoint_link.expand(obj, ctx)

        return links


class MemberRequestCommunityDashboardEndpointLink:
    """EndpointLink for community dashboard endpoint of request of member.

    WHY: A Member doesn't doesn't store its associated request in its entirety in same
         db/index entry (naturally). So the blunt approach of reusing Request dependent
         functionality is not possible without a high performance cost (to retrieve each
         full request) or an incomplete and error-prone faked interface.

         So we use a different approach instead. At the cost of not reusing the
         self_html link defined in the MemberRequest, we define the self_html links here
         in the context of a Member service call (Member JSON API). Contextual knowledge
         is leveraged to cut to the chase.
    """

    def __init__(self):
        """docstring."""

    def _select_link(self, obj, context):
        """Select EndpointLink corresponding to type of request of Member.

        :param obj: api.Member
        :param context: dict of context variables
        return EndpointLink
        """
        member = obj

        link_no_op = EndpointLink("", when=lambda obj, vars: False)

        # No member request link for active member or member without request
        # (added directly)
        if member.active or not member.get("request"):
            return link_no_op

        # Not all members may have a request with a type stored since the request type
        # was not stored originally. But in that case, because at this point we know the
        # Member is inactive and has a request without stored type, the request must be
        # an invitation (it's a legacy invitation).
        request_type_id = member["request"].get("type") or "community-invitation"

        if request_type_id == CommunityInvitation.type_id:
            # TODO: replace by
            #   invenio_app_rdm_requests.community_dashboard_invitation_view
            # when view implemented in invenio-app-rdm
            endpoint = "invenio_app_rdm_requests.community_dashboard_request_view"
        elif request_type_id == MembershipRequestRequestType.type_id:
            endpoint = "invenio_app_rdm_requests.community_dashboard_membership_request_view"  # noqa
        else:
            # In case something strange / future-proofing
            return link_no_op

        return EndpointLink(
            endpoint,
            params=["pid_value", "request_pid_value"],
            vars=lambda obj, vars: (
                vars.update(
                    # override the pid_value to use the community slug since this
                    # is a UI URL
                    pid_value=vars["community_slug"],
                    request_pid_value=str(member.request_id),
                ),
            ),
        )

    def should_render(self, obj, context):
        """Should render."""
        link = self._select_link(obj, context)
        return link.should_render(obj, context)

    def expand(self, obj, context):
        """Expand the link with obj and context."""
        link = self._select_link(obj, context)
        return link.expand(obj, context)
