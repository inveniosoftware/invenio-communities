# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from invenio_access.permissions import system_identity
from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_users_resources.proxies import current_users_service

from invenio_communities.proxies import current_communities


class CommunityMembersRecipient(RecipientGenerator):
    """Community member recipient generator for notifications."""

    def __init__(self, key, roles=None):
        """Ctor."""
        self.key = key
        self.roles = roles

    def __call__(self, notification, recipients: dict):
        """Fetch community and add members as recipients, based on roles."""
        community = dict_lookup(notification.context, self.key)
        members = current_communities.service.members.search(
            system_identity,
            community["id"],
            roles=self.roles,
        )

        user_ids = []
        for m in members:
            if m["member"]["type"] != "user":
                continue
            user_ids.append(m["member"]["id"])

        if not user_ids:
            return recipients

        users = current_users_service.read_many(system_identity, user_ids)
        for u in users:
            recipients[u["id"]] = Recipient(data=u)
        return recipients
