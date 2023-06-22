# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter
from invenio_users_resources.notifications.generators import UserRecipient


class CommunityInvitationSubmittedNotificationBuilder(NotificationBuilder):
    """Notification builder for community invitation submit event."""

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

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.receiver"),
    ]

    recipients = [
        UserRecipient(key="request.receiver"),
    ]

    recipient_filters = [
        UserPreferencesRecipientFilter(),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]
