# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from flask.views import MethodView
from webargs.flaskparser import use_kwargs
from webargs import fields, validate
from invenio_db import db

from functools import wraps
from flask import Blueprint, abort, request
from invenio_communities.api import CommunityMembersAPI, MembershipRequestCls
from flask_security import current_user
from sqlalchemy.exc import SQLAlchemyError
from invenio_records_rest.errors import PIDResolveRESTError

from .models import CommunityMember


def create_blueprint_from_app(app):
    community_members_rest_blueprint = Blueprint(
        'invenio_communities',
        __name__,
        template_folder="templates"
    )
    comm_view = CommunityMembersResource.as_view(
        'community_members_api'

    )
    community_members_rest_blueprint.add_url_rule(
        '/communities/<{0}:pid_value>/members'.format(
            'pid(comid,record_class="invenio_communities.api:Community",'
            'object_type="com")'),
        view_func=comm_view,
    )

    request_view = MembershipRequest.as_view(
        'community_requests_api'
    )
    community_members_rest_blueprint.add_url_rule(
        '/communities/requests/<membership_request_id>',
        view_func=request_view,
    )
    return community_members_rest_blueprint


def pass_community(f):
    """Decorator to retrieve persistent identifier and community.
    This decorator will resolve the ``pid_value`` parameter from the route
    pattern and resolve it to a PID and a community, which are then available in
    the decorated function as ``pid`` and ``community`` kwargs respectively.
    """
    @wraps(f)
    def inner(self, pid_value, *args, **kwargs):
        try:
            pid, community = request.view_args['pid_value'].data
            return f(self, pid=pid, community=community, *args, **kwargs)
        except SQLAlchemyError:
            raise PIDResolveRESTError(pid)

    return inner


class CommunityMembersResource(MethodView):
    post_args = {
        'role': fields.Raw(
            location='json',
            required=False,
            validate=[validate.OneOf(['M', 'A', 'C'])]
        ),# TODO add valid options
        'email': fields.Email(
            location='json',
            required=False
        ),
        'invite_type': fields.Raw(
            location='json',
            required=True,
            validate=[validate.OneOf(['invitation', 'request'])]
        )

    }
    # TODO: change invite_type name
    @use_kwargs(post_args)
    @pass_community
    def post(
            self, email=None, pid=None, community=None, role=None,
            invite_type=None, **kwargs):
        if invite_type == 'invitation':
            admin_ids = \
                [admin.id for admin in CommunityMember.get_admins(
                    community.id)]
            if not admin_ids:
                CommunityMembersAPI.set_default_admin(community)
            if int(current_user.get_id()) not in admin_ids:
                abort(404)
            CommunityMembersAPI.invite_member(community, email, role)
        elif invite_type == 'request':
            user_id = int(current_user.get_id())
            CommunityMembersAPI.join_community(user_id, community)
        db.session.commit()
        return 'Cool', 200

    @use_kwargs(post_args)
    @pass_community
    def put(
            self, membership_request_id, pid=None, community=None,
            role=None, **kwargs):
        existing_membership_req = MembershipRequest
        if existing_membership_req.is_invite:
            admin_ids = \
                [admin.id for admin in CommunityMember.get_admins(
                    community.id)]
            if int(current_user.get_id()) not in admin_ids:
                abort(404)
            existing_membership_req.role = role
        elif not existing_membership_req.is_invite:
            if existing_membership_req.user_id != int(current_user.get_id()):
                abort(404)
            existing_membership_req.role = role
        db.session.commit()
        return 'Cool', 200

    @pass_community
    def get(self, pid=None, community=None):
        CommunityMembersAPI.get_members(community.id).all()

    @pass_community
    def delete(self, user_id=None,  pid=None, community=None):
        CommunityMembersAPI.delete_member(community.id, user_id)
        db.session.commit()
        return 'Oki', 204


class MembershipRequest(MethodView):
    post_args = {
        'response': fields.Raw(
            location='json',
            required=True,
            validate=[validate.OneOf(['accept', 'decline'])]
        ),
        'role': fields.Raw(
            location='json',
            required=False,
            validate=[validate.OneOf(['M', 'A', 'C'])]
        )
    }

    #Implement rendering of UI page with the available options for handling the invitation.
    def get():
        pass

    @use_kwargs(post_args)
    def post(self, membership_request_id, response=None, role=None):
        if response == 'accept':
            MembershipRequestCls.accept_invitation(membership_request_id, role)
        else:
            MembershipRequestCls.decline_invitation(membership_request_id)

        db.session.commit()
        return 'Cool', 200
