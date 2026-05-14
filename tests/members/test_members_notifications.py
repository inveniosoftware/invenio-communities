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
    CommunityMembershipRequestAcceptedNotificationBuilder,
    CommunityMembershipRequestCancelledNotificationBuilder,
    CommunityMembershipRequestDeclinedNotificationBuilder,
    CommunityMembershipRequestExpiredNotificationBuilder,
    CommunityMembershipRequestSubmittedNotificationBuilder,
)


@pytest.fixture(scope="module")
def mail_ext(app):
    """Flask-Mail extension."""
    mail = app.extensions.get("mail")
    assert mail
    return mail


@pytest.fixture()
def mock_build_of_notification_builder(monkeypatch):
    """Factory fixture for setting up the builder under test and getting mock."""

    def _inner(builder_cls):
        """Do actual work."""
        # mock build to observe calls
        mock_build = MagicMock(side_effect=builder_cls.build)
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


def check_msg_subject_for(message, list_of_required_content):
    """Check mail subject for content."""
    for required in list_of_required_content:
        assert required in message.subject


def check_msg_content_for(message, list_of_required_content):
    """Check message body (incl. html) for content."""
    for required_content in list_of_required_content:
        for content in [message.body, message.html]:
            assert required_content in content


def get_msg_to_email(outbox, email):
    """Get outbox message sent to email."""
    msg = next((msg for msg in outbox if email in msg.send_to), None)
    assert msg
    return msg


#
# invenio-notification testcases
#
def test_community_invitation_submit_notification(
    app,
    clean_index,
    community,
    db,
    mail_ext,
    member_service,
    mock_build_of_notification_builder,
    new_user,
    owner,
    requests_service,
):
    """Test notifcation being built on community invitation submit."""

    # mock build to observe calls
    mock_build = mock_build_of_notification_builder(
        CommunityInvitationSubmittedNotificationBuilder
    )

    with mail_ext.record_messages() as outbox:
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
        request_id = inv["request"]["id"]
        assert f"/me/requests/{request_id}" in html
        assert "/account/settings/notifications" in html
        # role titles will be capitalized
        assert role.capitalize() in html
        assert "You have been invited to join" in html
        assert message in html
        assert community["metadata"]["title"] in html

    # decline to reset
    requests_service.execute_action(new_user.identity, request_id, "decline")
    with mail_ext.record_messages() as outbox:
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


def test_community_invitation_accept_notification(
    app,
    clean_index,
    community,
    db,
    mail_ext,
    member_service,
    members,
    mock_build_of_notification_builder,
    new_user,
    requests_service,
):
    """Test notifcation sent on community invitation accept."""

    owner = members["owner"]
    mock_build = mock_build_of_notification_builder(
        CommunityInvitationAcceptNotificationBuilder
    )

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]

    with mail_ext.record_messages() as outbox:
        request_id = inv["request"]["id"]
        # Validate that email was sent
        requests_service.execute_action(new_user.identity, request_id, "accept")
        # check notification is build on submit
        assert mock_build.called
        # community owner, manager get notified
        assert len(outbox) == 2
        html = outbox[0].html
        community_slug = community._record.slug
        assert f"/communities/{community_slug}/requests/{request_id}" in html
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
    app,
    clean_index,
    community,
    db,
    mail_ext,
    member_service,
    mock_build_of_notification_builder,
    new_user,
    owner,
    requests_service,
):
    """Test notifcation sent on community invitation cancel."""

    # mock build to observe calls
    mock_build = mock_build_of_notification_builder(
        CommunityInvitationCancelNotificationBuilder
    )

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }

    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]

    with mail_ext.record_messages() as outbox:
        request_id = inv["request"]["id"]
        # Validate that email was sent
        requests_service.execute_action(owner.identity, request_id, "cancel")
        # check notification is build on submit
        assert mock_build.called
        # invited user gets notified
        assert len(outbox) == 1
        html = outbox[0].html
        assert "/me/requests/{}".format(request_id) in html
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
    app,
    clean_index,
    community,
    db,
    mail_ext,
    member_service,
    members,
    mock_build_of_notification_builder,
    new_user,
    requests_service,
):
    """Test notifcation sent on community invitation decline."""

    owner = members["owner"]
    # mock build to observe calls
    mock_build = mock_build_of_notification_builder(
        CommunityInvitationDeclineNotificationBuilder
    )

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]

    with mail_ext.record_messages() as outbox:
        request_id = inv["request"]["id"]
        # Validate that email was sent
        # Added resp
        resp = requests_service.execute_action(new_user.identity, request_id, "decline")
        # check notification is build on submit
        assert mock_build.called
        # community owner, manager get notified
        assert len(outbox) == 2
        html = outbox[0].html
        community_slug = community._record.slug
        assert f"/communities/{community_slug}/requests/{request_id}" in html
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
    app,
    clean_index,
    community,
    db,
    mail_ext,
    member_service,
    members,
    mock_build_of_notification_builder,
    new_user,
    requests_service,
):
    """Test notifcation sent on community invitation decline."""

    owner = members["owner"]
    # mock build to observe calls
    mock_build = mock_build_of_notification_builder(
        CommunityInvitationExpireNotificationBuilder
    )

    role = "reader"
    data = {
        "members": [{"type": "user", "id": str(new_user.id)}],
        "role": role,
    }
    member_service.invite(owner.identity, community.id, data)
    res = member_service.search_invitations(owner.identity, community.id).to_dict()
    assert res["hits"]["total"] == 1
    inv = res["hits"]["hits"][0]

    with mail_ext.record_messages() as outbox:
        request_id = inv["request"]["id"]
        # Validate that email was sent
        requests_service.execute_action(system_identity, request_id, "expire")

        # check notification is build on submit
        assert mock_build.called
        # community owner, manager and invited user get notified
        assert len(outbox) == 3
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        manager = members["manager"]
        assert {new_user.email, manager.email, owner.email} == all_send_to

        # Relevant kinds of messages to test
        msg_to_manager = get_msg_to_email(outbox, manager.email)
        msg_to_invitee = get_msg_to_email(outbox, new_user.email)

        who = new_user.user.username or new_user.user.user_profile.get("full_name")
        title = community["metadata"]["title"]
        expiration_sentence = (
            f"The invitation for '@{who}' to join community '{title}' expired."
        )

        # Check manager content for key information
        community_slug = community._record.slug
        link = f"/communities/{community_slug}/requests/{request_id}"
        check_msg_content_for(msg_to_manager, [expiration_sentence, link])
        # Check invitee content for key information
        link = f"/me/requests/{request_id}"
        check_msg_content_for(msg_to_invitee, [expiration_sentence, link])


#
# membership request notification testcases
#
def test_request_membership_emits_notification(
    clean_index,  # instead of search_clear because module fixtures present
    community_open_to_membership_requests,
    create_member,
    create_user,
    db,
    mail_ext,
    member_service,
    mock_build_of_notification_builder,
):
    community = community_open_to_membership_requests
    mock_build = mock_build_of_notification_builder(
        CommunityMembershipRequestSubmittedNotificationBuilder
    )

    requester = create_user({"email": "requester@example.org", "username": "requester"})
    manager_user = create_user(
        {"email": "manager@example.org", "username": "manager_other"}
    )
    manager_member = create_member(
        community_id=community.id, user_id=manager_user.id, role="manager"
    )

    # Validate that notification email was sent
    with mail_ext.record_messages() as outbox:
        core_message = "membership request message"
        message = f"<p>{core_message}</p>"
        request_result = member_service.request_membership(
            requester.identity, community.id, {"message": message}
        )

        assert mock_build.called
        assert 2 == len(outbox)
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        assert {"manager@example.org", "owner@owner.org"} == all_send_to
        request_id = request_result.id
        community_slug = community._record.slug
        requester_name = requester.user.username or requester.user.user_profile.get(
            "full_name"
        )
        community_title = community["metadata"]["title"]
        role = "reader"
        # Since receivers of the request are community owners + managers
        # the link in the request is to the community request page
        link = f"/communities/{community_slug}/membership-requests/{request_id}"
        # Same content across all messages so just testing first
        # Check subject
        check_msg_subject_for(outbox[0], [requester_name, community_title])
        # Check content
        check_msg_content_for(outbox[0], [requester_name, community_title, role, link])
        # just checking html tags of message stripped in plain text
        # won't do for other tests
        assert core_message in outbox[0].body
        assert message not in outbox[0].body
        assert message in outbox[0].html


def test_cancel_membership_request_emits_notification(
    clean_index,  # instead of search_clear because module fixtures present
    community_open_to_membership_requests,
    create_member,
    create_user,
    db,
    mail_ext,
    member_service,
    mock_build_of_notification_builder,
    owner,
    requests_service,
):
    community = community_open_to_membership_requests
    mock_build = mock_build_of_notification_builder(
        CommunityMembershipRequestCancelledNotificationBuilder
    )
    requester = create_user({"email": "requester@example.org", "username": "requester"})
    manager_user = create_user(
        {"email": "manager@example.org", "username": "manager_other"}
    )
    manager_member = create_member(
        community_id=community.id, user_id=manager_user.id, role="manager"
    )
    message = "<p>membership request message</p>"
    request_result = member_service.request_membership(
        requester.identity, community.id, {"message": message}
    )

    # Validate that email was sent
    with mail_ext.record_messages() as outbox:
        requests_service.execute_action(requester.identity, request_result.id, "cancel")

        assert mock_build.called
        assert 2 == len(outbox)
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        assert {manager_user.email, owner.email} == all_send_to
        requester_name = requester.user.username or requester.user.user_profile.get(
            "full_name"
        )
        community_title = community["metadata"]["title"]
        community_slug = community._record.slug
        request_id = request_result.id
        # Since receivers of the request are community owners + managers
        # the link in the request is to the community request page
        link = f"/communities/{community_slug}/membership-requests/{request_id}"
        # Same content across all messages so just testing first
        # Check subject for key information
        check_msg_subject_for(outbox[0], [requester_name, community_title])
        # Check content for key information
        check_msg_content_for(outbox[0], [requester_name, community_title, link])


def test_decline_membership_request_emits_notification(
    clean_index,  # instead of search_clear because module fixtures present
    community_open_to_membership_requests,
    create_member,
    create_user,
    db,
    mail_ext,
    member_service,
    mock_build_of_notification_builder,
    owner,
    requests_service,
):
    community_result = community_open_to_membership_requests
    mock_build = mock_build_of_notification_builder(
        CommunityMembershipRequestDeclinedNotificationBuilder
    )
    requester = create_user({"email": "requester@example.org", "username": "requester"})
    manager_user = create_user(
        {"email": "manager@example.org", "username": "manager_other"}
    )
    manager_member = create_member(
        community_id=community_result.id, user_id=manager_user.id, role="manager"
    )
    message = "<p>membership request message</p>"
    request_result = member_service.request_membership(
        requester.identity, community_result.id, {"message": message}
    )

    # Validate that email was sent
    with mail_ext.record_messages() as outbox:
        requests_service.execute_action(
            manager_user.identity, request_result.id, "decline"
        )

        assert mock_build.called
        assert 1 == len(outbox)
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        assert {requester.user.email} == all_send_to

        community_title = community_result["metadata"]["title"]
        # Since receiver of the notification is the request's requester
        # the link in the notification email is to the user dashboard request
        link = f"/me/requests/{request_result.id}"
        # Check subject for key information
        check_msg_subject_for(outbox[0], [community_title])
        # Check content for key information
        check_msg_content_for(outbox[0], [community_title, link])


def test_accept_membership_request_emits_notification(
    clean_index,  # instead of search_clear because module fixtures present
    community_open_to_membership_requests,
    create_member,
    create_user,
    db,
    mail_ext,
    member_service,
    mock_build_of_notification_builder,
    owner,
    requests_service,
):
    community_result = community_open_to_membership_requests
    mock_build = mock_build_of_notification_builder(
        CommunityMembershipRequestAcceptedNotificationBuilder
    )
    requester = create_user({"email": "requester@example.org", "username": "requester"})
    manager_user = create_user(
        {"email": "manager@example.org", "username": "manager_other"}
    )
    manager_member = create_member(
        community_id=community_result.id, user_id=manager_user.id, role="manager"
    )
    message = "<p>membership request message</p>"
    request_result = member_service.request_membership(
        requester.identity, community_result.id, {"message": message}
    )

    # Validate that email was sent
    with mail_ext.record_messages() as outbox:
        requests_service.execute_action(
            manager_user.identity, request_result.id, "accept"
        )

        assert mock_build.called
        assert 1 == len(outbox)
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        assert {requester.user.email} == all_send_to

        community_title = community_result["metadata"]["title"]
        # Since receiver of the notification is the request's requester
        # the link in the notification email is to the user dashboard request
        link = f"/me/requests/{request_result.id}"
        # Check subject for key information
        check_msg_subject_for(outbox[0], [community_title])
        # Check content for key information
        check_msg_content_for(outbox[0], [community_title, link])


def test_expire_membership_request_emits_notification(
    clean_index,  # instead of search_clear because module fixtures present
    community_open_to_membership_requests,
    create_member,
    create_user,
    db,
    mail_ext,
    member_service,
    mock_build_of_notification_builder,
    owner,
    requests_service,
):
    community_result = community_open_to_membership_requests
    mock_build = mock_build_of_notification_builder(
        CommunityMembershipRequestExpiredNotificationBuilder
    )
    requester = create_user({"email": "requester@example.org", "username": "requester"})
    manager_user = create_user(
        {"email": "manager@example.org", "username": "manager_other"}
    )
    manager_member = create_member(
        community_id=community_result.id, user_id=manager_user.id, role="manager"
    )
    message = "<p>membership request message</p>"
    request_result = member_service.request_membership(
        requester.identity, community_result.id, {"message": message}
    )

    # Validate that email was sent
    with mail_ext.record_messages() as outbox:
        requests_service.execute_action(system_identity, request_result.id, "expire")

        assert mock_build.called
        assert 3 == len(outbox)
        all_send_to = reduce(lambda s, m: m.send_to | s, outbox, set())
        assert {requester.user.email, manager_user.email, owner.email} == all_send_to

        msg_to_manager = get_msg_to_email(outbox, manager_user.email)
        msg_to_requester = get_msg_to_email(outbox, requester.user.email)

        community_title = community_result["metadata"]["title"]
        community_slug = community_result._record.slug
        requester_name = requester.user.username or requester.user.user_profile.get(
            "full_name"
        )

        # Msg to manager
        # Check subject for key information
        check_msg_subject_for(msg_to_manager, [requester_name, community_title])
        # Check content for key information
        link = f"/communities/{community_slug}/membership-requests/{request_result.id}"
        check_msg_content_for(msg_to_manager, [requester_name, community_title, link])

        # Msg to requester
        # Check subject for key information
        check_msg_subject_for(msg_to_requester, [community_title])
        link = f"/me/requests/{request_result.id}"
        # Check content for key information
        check_msg_content_for(msg_to_requester, [community_title, link])
