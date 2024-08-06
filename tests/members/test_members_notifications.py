# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Northwestern University.
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from functools import reduce
from unittest.mock import MagicMock

import pytest
from invenio_access.permissions import system_identity
from invenio_notifications.proxies import current_notifications_manager

from invenio_communities.notifications.builders import (
    CommunityInvitationAcceptNotificationBuilder,
    CommunityInvitationCancelNotificationBuilder,
    CommunityInvitationDeclineNotificationBuilder,
    CommunityInvitationExpireNotificationBuilder,
    CommunityInvitationSubmittedNotificationBuilder,
    CommunityMembershipRequestAcceptNotificationBuilder,
    CommunityMembershipRequestCancelNotificationBuilder,
    CommunityMembershipRequestDeclineNotificationBuilder,
    CommunityMembershipRequestExpireNotificationBuilder,
    CommunityMembershipRequestSubmittedNotificationBuilder,
)


@pytest.fixture()
def setup_mock_of_notification_builder(monkeypatch):
    """Factory fixture for setting up the builder under test and getting mock."""

    def _inner(builder_cls):
        """Do actual work."""
        # mock build to observe calls
        mock_build = MagicMock()
        mock_build.side_effect = builder_cls.build
        monkeypatch.setattr(builder_cls, "build", mock_build)
        # setting specific builder for test case
        monkeypatch.setattr(
            current_notifications_manager,
            "builders",
            {
                **current_notifications_manager.builders,
                builder_cls.type: builder_cls,
            },
        )
        assert not mock_build.called
        return mock_build

    return _inner


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


#
# Membership requests cases
#


def test_request_membership_submit_notification(
    setup_mock_of_notification_builder,
    member_service,
    community,
    create_user,
    members,  # to make sure manager exists
    db,
    app,
    clean_index,  # instead of search_clear because module fixtures present
):
    mock_build = setup_mock_of_notification_builder(
        CommunityMembershipRequestSubmittedNotificationBuilder
    )
    mail = app.extensions.get("mail")
    assert mail
    new_user = create_user()

    # Validate that notification email was sent
    with mail.record_messages() as outbox:
        message = "<p>membership request message</p>"
        data = {
            "message": message,
        }
        request_result = member_service.request_membership(
            new_user.identity, community.id, data
        )

        assert mock_build.called
        assert 2 == len(outbox)
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        assert {"manager@manager.org", "owner@owner.org"} == all_send_to
        # Same content across all messages so just testing first
        html = outbox[0].html
        # Since receivers of the request are community owners + managers
        # the link in the request is to the community request page
        request_id = request_result.id
        assert f"/communities/{community.id}/requests/{request_id}" in html
        who = new_user.user.username or new_user.user.user_profile.get("full_name")
        title = community["metadata"]["title"]
        role = "Reader"
        assert f"'@{who}' wants to join the community '{title}' as '{role}'" in html
        assert message in html


def test_request_membership_cancel_notification(
    setup_mock_of_notification_builder,
    member_service,
    requests_service,
    community,
    members,  # to make sure manager exists
    create_user,
    db,
    app,
    clean_index,
):
    mock_build = setup_mock_of_notification_builder(
        CommunityMembershipRequestCancelNotificationBuilder
    )
    mail = app.extensions.get("mail")
    assert mail
    new_user = create_user()
    message = "<p>membership request message</p>"
    data = {
        "message": message,
    }
    request_result = member_service.request_membership(
        new_user.identity, community.id, data
    )

    # Validate that email was sent
    with mail.record_messages() as outbox:
        requests_service.execute_action(new_user.identity, request_result.id, "cancel")

        assert mock_build.called
        assert 2 == len(outbox)
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        assert {"manager@manager.org", "owner@owner.org"} == all_send_to
        html = outbox[0].html
        # Since receivers of the request are community owners + managers
        # the link in the request is to the community request page
        request_id = request_result.id
        assert f"/communities/{community.id}/requests/{request_id}" in html
        who = new_user.user.username or new_user.user.user_profile.get("full_name")
        title = community["metadata"]["title"]
        assert (
            f"The membership request for '@{who}' to join the community '{title}' was cancelled"
            in html
        )


def test_request_membership_decline_notification(
    setup_mock_of_notification_builder,
    member_service,
    requests_service,
    community,
    owner,
    members,
    create_user,
    db,
    app,
    clean_index,
):
    mock_build = setup_mock_of_notification_builder(
        CommunityMembershipRequestDeclineNotificationBuilder
    )
    mail = app.extensions.get("mail")
    assert mail
    new_user = create_user()
    message = "<p>membership request message</p>"
    data = {
        "message": message,
    }
    request_result = member_service.request_membership(
        new_user.identity, community.id, data
    )

    # Validate that email was sent
    with mail.record_messages() as outbox:
        requests_service.execute_action(owner.identity, request_result.id, "decline")

        assert mock_build.called
        assert 1 == len(outbox)
        assert {"user@example.org"} == outbox[0].send_to
        html = outbox[0].html
        # Since receivers of the request is the requester community owners + managers
        # the link in the request is to the community request page
        request_id = request_result.id
        assert f"/me/requests/{request_id}" in html
        title = community["metadata"]["title"]
        assert (
            f"The membership request to join the community '{title}' was declined"
            in html
        )


def test_request_membership_expire_notification(
    setup_mock_of_notification_builder,
    member_service,
    requests_service,
    community,
    members,
    create_user,
    db,
    app,
    clean_index,
):
    mock_build = setup_mock_of_notification_builder(
        CommunityMembershipRequestExpireNotificationBuilder
    )
    assert not mock_build.called
    mail = app.extensions.get("mail")
    assert mail
    new_user = create_user()
    message = "<p>membership request message</p>"
    data = {
        "message": message,
    }
    request_result = member_service.request_membership(
        new_user.identity, community.id, data
    )

    # Validate that email was sent
    with mail.record_messages() as outbox:
        requests_service.execute_action(system_identity, request_result.id, "expire")

        assert mock_build.called
        assert 3 == len(outbox)
        # owners, managers and requester should all be notified
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        # fmt: off
        assert (
            {"owner@owner.org" , "manager@manager.org", "user@example.org"} == all_send_to
        )
        # fmt: on
        html = outbox[0].html
        # TODO: Can we make it depend on receiver?
        # Since receivers of the request are community owners + managers + requester
        # the link in the request is to the community request page
        request_id = request_result.id
        assert f"/communities/{community.id}/requests/{request_id}" in html
        who = new_user.user.username or new_user.user.user_profile.get("full_name")
        title = community["metadata"]["title"]
        assert (
            f"The membership request for '@{who}' to join the community '{title}' expired"
            in html
        )


def test_request_membership_accept_notification(
    setup_mock_of_notification_builder,
    member_service,
    requests_service,
    community,
    owner,
    members,
    create_user,
    db,
    app,
    clean_index,
):
    mock_build = setup_mock_of_notification_builder(
        CommunityMembershipRequestAcceptNotificationBuilder
    )
    assert not mock_build.called
    mail = app.extensions.get("mail")
    assert mail
    new_user = create_user()
    message = "<p>membership request message</p>"
    data = {
        "message": message,
    }
    request_result = member_service.request_membership(
        new_user.identity, community.id, data
    )

    # Validate that email was sent
    with mail.record_messages() as outbox:
        requests_service.execute_action(owner.identity, request_result.id, "accept")

        assert mock_build.called
        assert 1 == len(outbox)
        # requester should be notified
        assert {"user@example.org"} == outbox[0].send_to
        html = outbox[0].html
        request_id = request_result.id
        assert f"/me/requests/{request_id}" in html
        title = community["metadata"]["title"]
        assert (
            f"The membership request to join the community '{title}' was accepted"
            in html
        )
