# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from abc import ABC

from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter
from invenio_users_resources.notifications.generators import UserRecipient

from invenio_communities.notifications.generators import CommunityMembersRecipient


class CommunityInvitationNotificationBuilder(NotificationBuilder):
    """Base notification builder for community invitation action."""

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
