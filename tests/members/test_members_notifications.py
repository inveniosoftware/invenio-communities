# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Northwestern University.
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from unittest.mock import MagicMock

from invenio_access.permissions import system_identity
from invenio_notifications.proxies import current_notifications_manager

from invenio_communities.notifications.builders import (
    CommunityInvitationAcceptNotificationBuilder,
    CommunityInvitationCancelNotificationBuilder,
    CommunityInvitationDeclineNotificationBuilder,
    CommunityInvitationExpireNotificationBuilder,
    CommunityInvitationSubmittedNotificationBuilder,
)


#
# invenio-notification testcases
#
def test_community_invitation_submit_notification(
    member_service,
    requests_service,
    community,
    owner,
    new_user,
    db,
    monkeypatch,
    app,
    clean_index,
):
    """Test notifcation being built on community invitation submit."""

    original_builder = CommunityInvitationSubmittedNotificationBuilder

    # mock build to observe calls
    mock_build = MagicMock()
    mock_build.side_effect = original_builder.build
    monkeypatch.setattr(original_builder, "build", mock_build)
    # setting specific builder for test case
    monkeypatch.setattr(
        current_notifications_manager,
        "builders",
        {
            **current_notifications_manager.builders,
            original_builder.type: original_builder,
        },
    )
    assert not mock_build.called

    mail = app.extensions.get("mail")
    assert mail

    with mail.record_messages() as outbox:
        # Validate that email was sent
        role = "reader"
        message = "<p>invitation message</p>"

        data = {
            "members": [{"type": "user", "id": str(new_user.id)}],
            "role": role,
            "message": message,
        }
        member_service.invite(owner.identity, community.id, data)
        # ensure that the invited user request has been indexed
        res = member_service.search_invitations(owner.identity, community.id).to_dict()
        assert res["hits"]["total"] == 1
        inv = res["hits"]["hits"][0]

        # check notification is build on submit
        assert mock_build.called
        assert len(outbox) == 1
        html = outbox[0].html
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(inv["request"]["id"]) in html
        # role titles will be capitalized
        assert role.capitalize() in html
        assert "You have been invited to join" in html
        assert message in html
        assert community["metadata"]["title"] in html

    # decline to reset
    requests_service.execute_action(new_user.identity, inv["request"]["id"], "decline")
    with mail.record_messages() as outbox:
        data = {
            "members": [{"type": "user", "id": str(new_user.id)}],
            "role": role,
        }
        # invite again without message
        member_service.invite(owner.identity, community.id, data)
        # ensure that the invited user request has been indexed
        res = member_service.search_invitations(owner.identity, community.id).to_dict()
        assert res["hits"]["total"] == 2
        inv = res["hits"]["hits"][1]

        # check notification is build on submit
        assert mock_build.called
        assert len(outbox) == 1
        html = outbox[0].html
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(inv["request"]["id"]) in html
        # role titles will be capitalized
        assert role.capitalize() in html
        assert "You have been invited to join" in html
        assert "with the following message:" not in html
        assert community["metadata"]["title"] in html


def test_community_invitation_accept_notification(
    member_service,
    requests_service,
    community,
    new_user,
    db,
    monkeypatch,
    app,
    members,
    clean_index,
):
    """Test notifcation sent on community invitation accept."""

    original_builder = CommunityInvitationAcceptNotificationBuilder

    owner = members["owner"]
    # mock build to observe calls
    mock_build = MagicMock()
    mock_build.side_effect = original_builder.build
    monkeypatch.setattr(original_builder, "build", mock_build)
    assert not mock_build.called

    mail = app.extensions.get("mail")
    assert mail

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]
    with mail.record_messages() as outbox:
        # Validate that email was sent
        requests_service.execute_action(
            new_user.identity, inv["request"]["id"], "accept"
        )
        # check notification is build on submit
        assert mock_build.called
        # community owner, manager get notified
        assert len(outbox) == 2
        html = outbox[0].html
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(inv["request"]["id"]) in html
        # role titles will be capitalized
        assert (
            "'@{who}' accepted the invitation to join your community '{title}'".format(
                who=new_user.user.username
                or new_user.user.user_profile.get("full_name"),
                title=community["metadata"]["title"],
            )
            in html
        )


def test_community_invitation_cancel_notification(
    member_service,
    requests_service,
    community,
    owner,
    new_user,
    db,
    monkeypatch,
    app,
    clean_index,
):
    """Test notifcation sent on community invitation cancel."""

    original_builder = CommunityInvitationCancelNotificationBuilder

    # mock build to observe calls
    mock_build = MagicMock()
    mock_build.side_effect = original_builder.build
    monkeypatch.setattr(original_builder, "build", mock_build)
    assert not mock_build.called

    mail = app.extensions.get("mail")
    assert mail

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }

    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]
    with mail.record_messages() as outbox:
        # Validate that email was sent
        requests_service.execute_action(owner.identity, inv["request"]["id"], "cancel")
        # check notification is build on submit
        assert mock_build.called
        # invited user gets notified
        assert len(outbox) == 1
        html = outbox[0].html
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(inv["request"]["id"]) in html
        # role titles will be capitalized
        assert (
            "The invitation for '@{who}' to join community '{title}' was cancelled".format(
                who=new_user.user.username
                or new_user.user.user_profile.get("full_name"),
                title=community["metadata"]["title"],
            )
            in html
        )


def test_community_invitation_decline_notification(
    member_service,
    requests_service,
    community,
    new_user,
    db,
    monkeypatch,
    app,
    members,
    clean_index,
):
    """Test notifcation sent on community invitation decline."""

    owner = members["owner"]
    original_builder = CommunityInvitationDeclineNotificationBuilder

    # mock build to observe calls
    mock_build = MagicMock()
    mock_build.side_effect = original_builder.build
    monkeypatch.setattr(original_builder, "build", mock_build)
    assert not mock_build.called

    mail = app.extensions.get("mail")
    assert mail

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]
    with mail.record_messages() as outbox:
        # Validate that email was sent
        # Added resp
        resp = requests_service.execute_action(
            new_user.identity, inv["request"]["id"], "decline"
        )
        # check notification is build on submit
        assert mock_build.called
        # community owner, manager get notified
        assert len(outbox) == 2
        html = outbox[0].html
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(inv["request"]["id"]) in html
        # role titles will be capitalized
        assert (
            "'@{who}' declined the invitation to join your community '{title}'".format(
                who=new_user.user.username
                or new_user.user.user_profile.get("full_name"),
                title=community["metadata"]["title"],
            )
            in html
        )


def test_community_invitation_expire_notification(
    member_service,
    requests_service,
    community,
    new_user,
    db,
    monkeypatch,
    app,
    members,
    clean_index,
):
    """Test notifcation sent on community invitation decline."""

    owner = members["owner"]
    original_builder = CommunityInvitationExpireNotificationBuilder

    # mock build to observe calls
    mock_build = MagicMock()
    mock_build.side_effect = original_builder.build
    monkeypatch.setattr(original_builder, "build", mock_build)
    assert not mock_build.called

    mail = app.extensions.get("mail")
    assert mail

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]
    with mail.record_messages() as outbox:
        # Validate that email was sent
        requests_service.execute_action(system_identity, inv["request"]["id"], "expire")

        # check notification is build on submit
        assert mock_build.called
        # community owner, manager and invited user get notified
        # TODO: Replace with equivalent
        assert len(outbox) == 3
        html = outbox[0].html
        # TODO: update to `req["links"]["self_html"]` when addressing https://github.com/inveniosoftware/invenio-rdm-records/issues/1327
        assert "/me/requests/{}".format(inv["request"]["id"]) in html
        # role titles will be capitalized
        assert (
            "The invitation for '@{who}' to join community '{title}' has expired.".format(
                who=new_user.user.username
                or new_user.user.user_profile.get("full_name"),
                title=community["metadata"]["title"],
            )
            in html
        )
