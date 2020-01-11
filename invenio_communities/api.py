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

    @property
    def schema(self):
        """JSON Schema for the community metadata."""
        return current_app.config.get(
            'COMMUNITY_SCHEMA', 'communities/communities-v1.0.0.json')

    def delete(self, force=True):  # NOTE: By default hard-deleted
        """Delete a community."""
        return super(Community, self).delete(force=force)


class CommunityMembersCls(object):

    @classmethod
    def invite_member(cls, community, pid_id, email, role):
        MembershipRequests.create(pid_id, role, True)
        send_email_invitation(pid_id, email, community, role)
        return 'Ok'

    @classmethod
    def join_community(cls, community, pid_id, email, role):
        MembershipRequests.create(pid_id, role, False)
        send_email_invitation(pid_id, email, community, role)
        return 'Ok'

    @classmethod
    def get_members(cls, pid_id):
        community_members = CommunityMembers.query.filter_by(pid_id).all()
        return community_members


    @classmethod
    def delete_member(cls, pid_id):
        community_members = CommunityMembers.query.filter_by(pid_id).all()
        return community_members


class MembershipRequestCls():

    @classmethod
    def accept_invitation(cls, token):
        request_id = EmailConfirmationSerializer.load_token(token).get('id')
        if not request_id:
            raise(Exception)
        request = MembershipRequests.query.get(request_id)
        if request.is_invite and not request.user_id:
            request.user_id = int(current_user.get_id())
        elif request.user_id != int(current_user.get_id()):
            # TBD if needed.
            abort(404)
        community_member = CommunityMembers.create_or_modify(request)
        return community_member

    @classmethod
    def decline_invitation(cls, token):
        request_id = EmailConfirmationSerializer.load_token(token).get('id')
        MembershipRequests.delete(request_id)
        pass
