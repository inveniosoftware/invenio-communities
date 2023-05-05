# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Notification related tests."""

from invenio_notifications.models import Notification

from invenio_communities.notifications.generators import CommunityMembersRecipient


def test_user_recipient_generator(community, members):
    """Add community members based on provided roles."""
    n = Notification(
        type="",
        context={"community": community.to_dict()},
    )

    # get all members of the community
    recipients = {}
    CommunityMembersRecipient(key="community")(n, recipients=recipients)
    assert len(recipients) == len(members)
    assert [u.id for u in members.values()] == list(recipients.keys())

    # get owner and reader only
    recipients = {}
    CommunityMembersRecipient(key="community", roles=["owner", "reader"])(
        n, recipients=recipients
    )
    assert len(recipients) == 2
    assert [members["owner"].id, members["reader"].id] == list(recipients)
