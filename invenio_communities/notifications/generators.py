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
from invenio_search.engine import dsl
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
        filter_ = dsl.Q("terms", **{"role": self.roles}) if self.roles else None

        members = current_communities.service.members.scan(
            system_identity,
            community["id"],
            extra_filter=filter_,
        )

        user_ids = []
        for m in members:
            # TODO: add support for groups
            if m["member"]["type"] != "user":
                continue
            user_ids.append(m["member"]["id"])

        if not user_ids:
            return recipients

        filter_ = dsl.Q("terms", **{"id": user_ids})
        users = current_users_service.scan(system_identity, extra_filter=filter_)
        for u in users:
            recipients[u["id"]] = Recipient(data=u)
        return recipients
