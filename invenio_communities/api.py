# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

from flask_security import current_user
from flask import current_app, abort
from sqlalchemy.exc import IntegrityError
from werkzeug.local import LocalProxy

from invenio_db import db
from invenio_records.api import Record
from invenio_accounts.models import User

from .models import CommunityMetadata, CommunityMembers, MembershipRequests
from .email import send_email_invitation, EmailConfirmationSerializer


class Community(Record):
    """Define API for community creation and manipulation."""

    # TODO: Communities model doesn't have versioninig, some methods from
    # "invenio_records.api.RecordBase" have to be overridden/removed
    model_cls = CommunityMetadata

    schema = LocalProxy(lambda: current_app.config.get(
            'COMMUNITY_SCHEMA', 'communities/communities-v1.0.0.json'))

    def delete(self, force=False):
        """Delete a community."""
        with db.session.begin_nested():
            if force:
                db.session.delete(self.model)
            else:
                self.model.delete()

        return self


class CommunityMembersCls(object):

    @classmethod
    def invite_member(cls, community, email, role):
        admin_ids = \
            [admin.id for admin in CommunityMembers.get_admins(community.id)]
        if int(current_user.get_id()) not in admin_ids:
            abort(404)
        membership_request = MembershipRequests.create(
            community.id, True, role=role)
        send_email_invitation(membership_request.id, email, community, role)
        return 'Ok'

    @classmethod
    def join_community(cls, community):
        user_id = int(current_user.get_id())
        membership_request = MembershipRequests.create(
            community.id, False, user_id=user_id)
        community_admins = CommunityMembers.get_admins(community.id)
        admin_emails = [admin.email for admin in community_admins]
        send_email_invitation(membership_request.id, admin_emails, community)
        return 'Ok'

    @classmethod
    def get_members(cls, comm_id):
        community_members = CommunityMembers.query.filter_by(comm_id=comm_id).all()
        return community_members


    @classmethod
    def delete_member(cls, comm_id):
        community_members = CommunityMembers.query.filter_by(comm_id=comm_id).all()
        return community_members


class MembershipRequestCls():

    @classmethod
    def accept_invitation(cls, token, role=None):
        request_id = EmailConfirmationSerializer().load_token(token).get('id')
        if not request_id:
            raise(Exception)
        request = MembershipRequests.query.get(request_id)
        if request.is_invite and not request.user_id:
            if current_user.get_id():
                request.user_id = int(current_user.get_id())
        elif int(current_user.get_id()): #add check for permissions on who is handling requesests
            request.role = role
        else:
            # TBD if needed.
            abort(404)
        community_member = CommunityMembers.create_or_modify(request)
        return community_member

    @classmethod
    def decline_invitation(cls, token):
        request_id = EmailConfirmationSerializer.load_token(token).get('id')
        MembershipRequests.delete(request_id)
        pass
