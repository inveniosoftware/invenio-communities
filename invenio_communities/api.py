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

from .models import CommunityMetadata, CommunityMember, MembershipRequest
from .email import send_email_invitation


class Community(Record):
    """Define API for community creation and manipulation."""

    # TODO: Communities model doesn't have versioninig, some methods from
    # "invenio_records.api.RecordBase" have to be overridden/removed
    model_cls = CommunityMetadata

    schema = LocalProxy(lambda: current_app.config.get(
            'COMMUNITY_SCHEMA', 'communities/communities-v1.0.0.json'))


    @classmethod
    def create(cls, data, id_=None, **kwargs):
        r"""Create a new record instance and store it in the database.

        #. Send a signal :data:`invenio_records.signals.before_record_insert`
           with the new record as parameter.

        #. Validate the new record data.

        #. Add the new record in the database.

        #. Send a signal :data:`invenio_records.signals.after_record_insert`
           with the new created record as parameter.

        :Keyword Arguments:
          * **format_checker** --
            An instance of the class :class:`jsonschema.FormatChecker`, which
            contains validation rules for formats. See
            :func:`~invenio_records.api.RecordBase.validate` for more details.

          * **validator** --
            A :class:`jsonschema.IValidator` class that will be used to
            validate the record. See
            :func:`~invenio_records.api.RecordBase.validate` for more details.

        :param data: Dict with the record metadata.
        :param id_: Specify a UUID to use for the new record, instead of
                    automatically generated.
        :returns: A new :class:`Record` instance.
        """
        with db.session.begin_nested():
            community = cls(data)

            community.validate(**kwargs)

            community.model = cls.model_cls(id=id_, json=community)

            db.session.add(community.model)

            CommunityMembersAPI.set_default_admin(community.model)

        return community


    def delete(self, force=False):
        """Delete a community."""
        with db.session.begin_nested():
            if force:
                db.session.delete(self.model)
            else:
                self.model.delete()

        return self





class CommunityMembersAPI(object):

    @classmethod
    def invite_member(cls, community, email, role, send_email=True):
        existing_membership_req = MembershipRequest.query.filter_by(
                    comm_id=community.comm_id,
                    email=email
                    ).one_or_none()
        if existing_membership_req:
            abort(400, 'This is an already existing relationship.')
        membership_request = MembershipRequest.create(
            community.id, True, role=role, email=email)
        if send_email:
            send_email_invitation(
                membership_request.id, email, community, role)
        return membership_request

    @classmethod
    def join_community(cls, user_id, community, send_email=True):
        membership_request = MembershipRequest.create(
            community.id, False, user_id=user_id)
        if send_email:
            community_admins = CommunityMember.get_admins(community.id)
            admin_emails = [admin.email for admin in community_admins]
            send_email_invitation(membership_request.id, admin_emails, community)
        return membership_request

    @classmethod
    def get_members(cls, pid_id):
        return CommunityMember.get_members()

    @classmethod
    def delete_member(cls, comm_id, user_id):
        CommunityMember.delete(comm_id, user_id)

    @classmethod
    def set_default_admin(cls, community):
        CommunityMember.create(
            comm_id=community.id,
            user_id=community.json['created_by'],
            role='A')


class MembershipRequestCls():

    @classmethod
    def accept_invitation(cls, membership_request_id, role=None):
        if not membership_request_id:
            raise(Exception)
        request = MembershipRequest.query.get(membership_request_id)
        if request.is_invite and not request.user_id:
            if current_user.get_id():
                request.user_id = int(current_user.get_id())
        elif int(current_user.get_id()): #add check for permissions on who is handling requesests
            request.role = role
        else:
            # TBD if needed.
            abort(404)
        community_member = CommunityMember.create_from_object(request)
        return community_member

    @classmethod
    def decline_invitation(cls, membership_request_id):
        MembershipRequest.delete(membership_request_id)
        pass
