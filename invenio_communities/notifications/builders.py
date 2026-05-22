# SPDX-FileCopyrightText: 2024-2025 CERN.
# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Notification related utils for notifications."""

from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend
from invenio_requests.notifications.filters import UserRecipientFilter
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter
from invenio_users_resources.notifications.generators import UserRecipient

from invenio_communities.notifications.generators import CommunityMembersRecipient


class BaseNotificationBuilder(NotificationBuilder):
    """Base notification builder for community notification."""

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.receiver"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class CommunityInvitationNotificationBuilder(BaseNotificationBuilder):
    """Base notification builder for community invitation action."""


class CommunityInvitationSubmittedNotificationBuilder(
    CommunityInvitationNotificationBuilder
):
    """Notification builder for community invitation submit action."""

    type = "community-invitation.submit"

    @classmethod
    def build(cls, request, role, message=None):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "role": role,
                "message": message,
            },
        )

    recipients = [
        UserRecipient(key="request.receiver"),
    ]


class CommunityInvitationAcceptNotificationBuilder(
    CommunityInvitationNotificationBuilder
):
    """Notification builder for community invitation accept action."""

    type = "community-invitation.accept"

    @classmethod
    def build(cls, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )

    recipients = [
        CommunityMembersRecipient(key="request.created_by", roles=["owner", "manager"]),
    ]


class CommunityInvitationCancelNotificationBuilder(
    CommunityInvitationNotificationBuilder
):
    """Notification builder for community invitation cancel action."""

    type = "community-invitation.cancel"

    @classmethod
    def build(cls, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )

    recipients = [
        UserRecipient(key="request.receiver"),
    ]


class CommunityInvitationDeclineNotificationBuilder(
    CommunityInvitationNotificationBuilder
):
    """Notification builder for community invitation decline action."""

    type = "community-invitation.decline"

    @classmethod
    def build(cls, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )

    recipients = [
        CommunityMembersRecipient(key="request.created_by", roles=["owner", "manager"]),
    ]


class CommunityInvitationExpireNotificationBuilder(
    CommunityInvitationNotificationBuilder
):
    """Notification builder for community invitation expire action."""

    type = "community-invitation.expire"

    @classmethod
    def build(cls, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )

    recipients = [
        CommunityMembersRecipient(key="request.created_by", roles=["owner", "manager"]),
        UserRecipient(key="request.receiver"),
    ]


class CommunityMembershipRequestNotificationBuilder(BaseNotificationBuilder):
    """Base notification builder for community membership-request action."""

    type = "community-membership-request"

    @classmethod
    def build(cls, request, message=None):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )


class CommunityMembershipRequestSubmittedNotificationBuilder(
    CommunityMembershipRequestNotificationBuilder
):
    """Notification builder for membership request submitted."""

    type = f"{CommunityMembershipRequestNotificationBuilder.type}.submit"

    @classmethod
    def build(cls, request, role, message=None):
        """Build notification with request context.

        :param request: api.Request
        :param role: string
        :param message: string
        """
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "role": role,
                "message": message,
            },
        )

    recipients = [
        CommunityMembersRecipient(key="request.receiver", roles=["owner", "manager"]),
    ]


class CommunityMembershipRequestCancelledNotificationBuilder(
    CommunityMembershipRequestNotificationBuilder
):
    """Notification builder for membership request cancelled."""

    type = f"{CommunityMembershipRequestNotificationBuilder.type}.cancel"
    recipients = [
        CommunityMembersRecipient(key="request.receiver", roles=["owner", "manager"]),
    ]


class CommunityMembershipRequestAcceptedNotificationBuilder(
    CommunityMembershipRequestNotificationBuilder
):
    """Notification builder for membership request accepted."""

    type = f"{CommunityMembershipRequestNotificationBuilder.type}.accept"

    recipients = [
        UserRecipient(key="request.created_by"),
    ]


class CommunityMembershipRequestDeclinedNotificationBuilder(
    CommunityMembershipRequestNotificationBuilder
):
    """Notification builder for membership request declined."""

    type = f"{CommunityMembershipRequestNotificationBuilder.type}.decline"

    recipients = [
        UserRecipient(key="request.created_by"),
    ]


class CommunityMembershipRequestExpiredNotificationBuilder(
    CommunityMembershipRequestNotificationBuilder
):
    """Notification builder for membership request expired."""

    type = f"{CommunityMembershipRequestNotificationBuilder.type}.expire"

    recipients = [
        UserRecipient(key="request.created_by"),
        CommunityMembersRecipient(key="request.receiver", roles=["owner", "manager"]),
    ]


#
# Subcommunity request
#
class SubCommunityBuilderBase(BaseNotificationBuilder):
    """Base notification builder for subcommunity requests."""

    type = "subcommunity-request"

    context = [
        EntityResolve("request"),
        EntityResolve("request.created_by"),
        EntityResolve("request.topic"),
        EntityResolve("request.receiver"),
        EntityResolve("executing_user"),
    ]

    @classmethod
    def build(cls, identity, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "executing_user": EntityResolverRegistry.reference_identity(identity),
            },
        )

    recipients = [
        CommunityMembersRecipient("request.created_by", roles=["owner", "manager"]),
        CommunityMembersRecipient("request.receiver", roles=["owner", "manager"]),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        # Don't send notifications to the user performing the action
        UserRecipientFilter("executing_user"),
    ]


class SubCommunityCreate(SubCommunityBuilderBase):
    """Notification builder for subcommunity request creation."""

    type = f"{SubCommunityBuilderBase.type}.create"

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        # TODO: We exceptionally DON'T filter out the executing user here, because we
        # don't have a clear place where they can see the created request.
        # See also: https://github.com/inveniosoftware/invenio-communities/issues/1158
        # UserRecipientFilter("executing_user"),
    ]


class SubCommunityAccept(SubCommunityBuilderBase):
    """Notification builder for subcommunity request accept."""

    type = f"{SubCommunityBuilderBase.type}.accept"


class SubCommunityDecline(SubCommunityBuilderBase):
    """Notification builder for subcommunity request decline."""

    type = f"{SubCommunityBuilderBase.type}.decline"


class SubComInvitationBuilderBase(SubCommunityBuilderBase):
    """Base notification builder for subcommunity invitation requests."""

    type = "subcommunity-invitation-request"

    context = [
        EntityResolve("request"),
        EntityResolve("request.created_by"),
        EntityResolve("request.receiver"),
        EntityResolve("executing_user"),
    ]


class SubComInvitationCreate(SubComInvitationBuilderBase):
    """Notification builder for subcommunity request creation."""

    type = f"{SubComInvitationBuilderBase.type}.create"

    context = [
        EntityResolve("request"),
        EntityResolve("request.created_by"),
        EntityResolve("request.receiver"),
        # EntityResolve("executing_user") creating via script only for now
    ]

    recipients = [
        CommunityMembersRecipient("request.receiver", roles=["owner", "manager"]),
    ]


class SubComInvitationAccept(SubComInvitationBuilderBase):
    """Notification builder for subcommunity request accept."""

    type = f"{SubComInvitationBuilderBase.type}.accept"

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        # Don't send notifications to the user performing the action
        UserRecipientFilter("executing_user"),
    ]


class SubComInvitationDecline(SubComInvitationBuilderBase):
    """Notification builder for subcommunity request decline."""

    type = f"{SubComInvitationBuilderBase.type}.decline"

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        # Don't send notifications to the user performing the action
        UserRecipientFilter("executing_user"),
    ]


class SubComInvitationExpire(SubComInvitationBuilderBase):
    """Notification builder for subcommunity invitation expire."""

    type = f"{SubComInvitationBuilderBase.type}.expire"

    context = [
        EntityResolve("request"),
        EntityResolve("request.created_by"),
        EntityResolve("request.receiver"),
    ]

    recipients = [
        CommunityMembersRecipient("request.receiver", roles=["owner", "manager"]),
    ]


#
# Comments
#
class SubComCommentNotificationBuilderBase(SubCommunityBuilderBase):
    """Notification builder for comment request event creation."""

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.receiver"),
        EntityResolve(key="request_event"),
        EntityResolve(key="request_event.created_by"),
    ]

    @classmethod
    def build(cls, request, request_event):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "request": EntityResolverRegistry.reference_entity(request),
                "request_event": EntityResolverRegistry.reference_entity(request_event),
            },
        )

    recipient_filters = [
        # do not send notification to user creating the comment
        UserRecipientFilter(key="request_event.created_by"),
        UserPreferencesRecipientFilter(),
    ]


class SubComReqCommentNotificationBuilder(SubComCommentNotificationBuilderBase):
    """Notification builder for comment request event creation."""

    type = f"comment-{SubCommunityBuilderBase.type}.create"


class SubComInvCommentNotificationBuilder(SubComCommentNotificationBuilderBase):
    """Notification builder for comment request event creation."""

    type = f"comment-{SubComInvitationBuilderBase.type}.create"
