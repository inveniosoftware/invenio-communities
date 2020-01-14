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

from flask import Blueprint
from invenio_communities.api import CommunityMembersCls, MembershipRequestCls
from flask_security import current_user

def create_blueprint_from_app(app):
    community_members_rest_blueprint = Blueprint(
        'invenio_communities',
        __name__,
        url_prefix="",
        template_folder="./templates"
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
        '/communities/requests/<token>',
        view_func=request_view,
    )
    return community_members_rest_blueprint


class CommunityMembersResource(MethodView):
    post_args = {
        'role': fields.Raw(
            location='json',
            required=False,
            validate=[validate.OneOf(['M', 'A', 'C'])]
        ),# add valid options
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
    def post(self, email=None, pid_value=None, role=None, invite_type=None):
        pid, community = pid_value.data
        if invite_type == 'invitation':
            CommunityMembersCls.invite_member(community, email, role)
        elif invite_type == 'request':
            CommunityMembersCls.join_community(community)
        db.session.commit()
        return 'Cool', 200

    def get(self, pid_value=None):
        pid, community = pid_value.data

        CommunityMembersCls.get_members(pid.id)

    def delete(self, user_id=None, pid_value=None):
        pid, community = pid_value.data
        CommunityMembersCls.delete_member(pid.id, user_id)
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
    def post(self, token=None, response=None, role=None):
        if response == 'accept':
            MembershipRequestCls.accept_invitation(token, role)
        else:
            MembershipRequestCls.decline_invitation(token)

        db.session.commit()
        return 'Cool', 200
