# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

from invenio_communities.members.models import CommunityMember, \
    CommunityMetadata, MembershipRequest
from invenio_communities.utils import send_invitation_email


class CommunityMembersAPI(object):

    @classmethod
    def invite_member(cls, community, email, role, send_email=True):
        membership_request = MembershipRequest.create(
            community.id, True, role=role, email=email)
        if send_email:
            send_invitation_email(membership_request, [email], community)
        return membership_request

    @classmethod
    def join_community(cls, user_id, email, community, send_email=True):
        membership_request = MembershipRequest.create(
            community.id, False, user_id=user_id, email=email)
        if send_email:
            community_admins = CommunityMember.get_admins(community.id)
            admin_emails = [admin.email for admin in community_admins]
            send_invitation_email(
                membership_request, admin_emails, community)
        return membership_request

    @classmethod
    def get_members(cls, comm_id):
        return CommunityMember.get_members(comm_id)

    @classmethod
    def delete_member(cls, comm_id, user_id):
        CommunityMember.delete(comm_id, user_id)

    @classmethod
    def set_default_admin(cls, community):
        CommunityMember.create(
            comm_id=community.id,
            user_id=community.json['created_by'],
            role='A')

    @classmethod
    def modify_membership(cls, user_id, comm_id, role):
        member = CommunityMember.query.filter_by(
            comm_id=comm_id, user_id=user_id).one_or_none()
        if member:
            member.role = role
            return member
        else:
            return None

    # TODO: implement as contains in the future refactor
    @classmethod
    def has_member(cls, community, user):
        # TODO: maybe int(user_id)
        return CommunityMember.query.filter_by(
            comm_id=community.id, user_id=user.id).one_or_none()

    @classmethod
    def has_admin(cls, community, user):
        # TODO: maybe int(user_id)
        return CommunityMember.query.filter_by(
            comm_id=community.id, user_id=user.id, role='A').one_or_none()


class MembershipRequestAPI(object):

    @classmethod
    def get_invitation(cls, membership_request_id):
        request = MembershipRequest.query.get(membership_request_id)
        community = CommunityMetadata.query.get(request.comm_id)
        return (request, community)

    @classmethod
    def accept_invitation(cls, request, role=None, user_id=None):
        if request.is_invite and not request.user_id:
            request.user_id = user_id
        else:  # add check for permissions on who is handling requesests
            request.role = role
        community_member = CommunityMember.create_from_object(request)
        return community_member

    @classmethod
    def decline_or_cancel_invitation(cls, membership_request_id):
        MembershipRequest.delete(membership_request_id)
        pass

    @classmethod
    def modify_membership_request(cls, comm_id, email, role):
        existing_membership_req = MembershipRequest.query.filter_by(
                comm_id=comm_id,
                email=email
                ).one_or_none()
        if existing_membership_req:
            existing_membership_req.role = role
            return existing_membership_req
        else:
            return None

    @classmethod
    def get_community_outgoing_requests(
            cls, comm_id, page_size=20, page_number=0):
        incoming_count = MembershipRequest.query.filter_by(
            is_invite=True, comm_id=comm_id).count()
        incoming_requests = MembershipRequest.query.filter_by(
            is_invite=True, comm_id=comm_id)[page_number*page_size:page_size]
        return (incoming_count, incoming_requests)

    @classmethod
    def get_community_incoming_requests(
            cls, comm_id, page_size=20, page_number=0):
        outgoing_count = MembershipRequest.query.filter_by(
            is_invite=False, comm_id=comm_id).count()
        outgoing_requests = MembershipRequest.query.filter_by(
            is_invite=False, comm_id=comm_id)[page_number*page_size:page_size]
        return (outgoing_count, outgoing_requests)
