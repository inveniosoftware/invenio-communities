# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from flask_menu import current_menu
from flask.views import MethodView
from webargs import ValidationError, fields, validate
from webargs.flaskparser import FlaskParser as FlaskParserBase
from invenio_db import db

from functools import wraps
from flask import Blueprint, abort, request, render_template, jsonify
from flask_security import current_user
from sqlalchemy.exc import SQLAlchemyError
from invenio_records_rest.errors import PIDResolveRESTError
from invenio_rest.errors import FieldError, RESTValidationError


from .api import CommunityMembersAPI, MembershipRequestAPI
from .models import CommunityMember, MembershipRequest
from ..views import pass_community, pass_community_function, use_args, use_kwargs


def create_blueprint_from_app(app):
    """Blueprint creating function."""
    community_members_rest_blueprint = Blueprint(
        'invenio_communities_members',
        __name__,
        template_folder="../templates",
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

    request_management_view = CommunityRequestsResource.as_view(
        'community_requests_management_api'

    )
    community_members_rest_blueprint.add_url_rule(
        '/communities/<{0}:pid_value>/members/requests'.format(
            'pid(comid,record_class="invenio_communities.api:Community",'
            'object_type="com")'),
        view_func=request_management_view,
    )

    request_view = MembershipRequestResource.as_view(
        'community_requests_api'
    )
    community_members_rest_blueprint.add_url_rule(
        '/communities/members/requests/<membership_request_id>',
        view_func=request_view,
    )
    return community_members_rest_blueprint


class CommunityMembersResource(MethodView):
    """Resource for creating, listing and removing community memberships."""

    post_args = {
        'role': fields.Raw(
            location='json',
            required=False,
            validate=[validate.OneOf(['M', 'A', 'C'])]
        ),
        'email': fields.Email(
            location='json',
            required=False
        ),
        'request_type': fields.Raw(
            location='json',
            required=True,
            validate=[validate.OneOf(['invitation', 'request'])]
        )

    }

    put_args = {
        'role': fields.Raw(
            location='json',
            required=False,
            validate=[validate.OneOf(['M', 'A', 'C'])]
        ),
        'user_id': fields.Raw(
            location='json',
            required=False
        ),
        'email': fields.Email(
            location='json',
            required=False
        ),
    }

    delete_args = {
        'user_id': fields.Raw(
            location='query',
            required=False
        ),
    }

    @use_kwargs(post_args)
    @pass_community
    def post(self, email=None, pid=None, community=None, role=None,
             request_type=None, **kwargs):
        """Join a community or invite a user to it."""
        if request_type == 'invitation':
            admin_ids = \
                [admin.user.id for admin in CommunityMember.get_admins(
                    community.id)]
            if int(current_user.get_id()) not in admin_ids:
                abort(404)
            existing_membership_req = MembershipRequest.query.filter_by(
                    comm_id=community.id,
                    email=email
                    ).one_or_none()
            if existing_membership_req:
                abort(400, 'This is an already existing relationship.')
            CommunityMembersAPI.invite_member(community, email, role)
        elif request_type == 'request':
            user_id = int(current_user.get_id())
            email = current_user.email
            CommunityMembersAPI.join_community(user_id, email, community)
        db.session.commit()
        return 'Succesfully Invited', 200

    @pass_community
    def get(self, pid=None, community=None):
        """List the community members."""
        admin_ids = \
            [admin.user.id for admin in CommunityMember.get_admins(
                community.id)]
        if int(current_user.get_id()) not in admin_ids:
            abort(404)
        ui_members = []
        for member in CommunityMembersAPI.get_members(community.id).all():
            add_member = {}
            add_member['user_id'] = str(member.user_id)
            add_member['email'] = member.user.email
            add_member['role'] = str(member.role.title)
            ui_members.append(add_member)
        return jsonify(ui_members), 200

    @use_kwargs(delete_args)
    @pass_community
    def delete(self, user_id=None, community=None, pid=None):
        """Remove a member from a community."""
        admin_ids = \
            [admin.user.id for admin in CommunityMember.get_admins(
                community.id)]
        if int(current_user.get_id()) not in admin_ids:
            abort(404)
        CommunityMembersAPI.delete_member(community.id, user_id)
        db.session.commit()
        return 'Succesfully removed', 204


class CommunityRequestsResource(MethodView):
    """Resource to list community membership requests."""

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

    @pass_community
    def get(self, community=None, pid=None, outgoing_only=False,
            incoming_only=False, page_size=20, page=0):
        """List all the community membership requests."""
        admin_ids = \
            [admin.user.id for admin in CommunityMember.get_admins(
                community.id)]
        if int(current_user.get_id()) not in admin_ids:
            abort(404)
        response_object = {}
        if not outgoing_only:
            count, requests = \
                MembershipRequestAPI.get_community_incoming_requests(
                    community.id, page_size=page_size)
            response_object['inc_count'] = count
            response_object['inc_requests'] = []
            for req in requests:
                response_object['inc_requests'].append({
                    'email': req.email,
                    'req_id': req.id
                })
        if not incoming_only:
            count, requests = \
                MembershipRequestAPI.get_community_outgoing_requests(
                    community.id, page_size=page_size)
            response_object['out_count'] = count
            response_object['out_requests'] = []
            for req in requests:
                response_object['out_requests'].append({
                    'email': req.email,
                    'req_id': req.id,
                    'role': str(req.role.title)
                })
        return jsonify(response_object), 200


class MembershipRequestResource(MethodView):
    """Resource to view and handle membership requests."""

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

    put_args = {
        'role': fields.Raw(
            location='json',
            required=True,
            validate=[validate.OneOf(['M', 'A', 'C'])]
        )
    }

    def get(self, membership_request_id):
        """Get the information for a membership request."""
        request, community = MembershipRequestAPI.get_invitation(
            membership_request_id)
        response_object = {}
        response_object['community_name'] = community.json['title']
        response_object['community_id'] = community.json['id']
        response_object['role'] = str(request.role.title)
        return jsonify(response_object), 200

    @use_kwargs(post_args)
    def post(self, membership_request_id, response=None, role=None):
        """Accept or reject a membership request."""
        if not current_user.is_authenticated:
            abort(404)
        user_id = int(current_user.get_id())
        request = MembershipRequest.query.get(membership_request_id)
        if not request.is_invite:  # and current_user.email == request.email):
            community_admins = [admin.user.id for admin in
                                CommunityMember.get_admins(request.comm_id)]
            if not (user_id in community_admins and not request.is_invite):
                abort(404)
        if response == 'accept':
            MembershipRequestAPI.accept_invitation(
                request, role, user_id)
            db.session.commit()
            return 'Succesfully accepted.', 200
        else:
            MembershipRequestAPI.decline_or_cancel_invitation(request.id)
            db.session.commit()
            return 'Succesfully rejected.', 200

    @use_kwargs(put_args)
    def put(self, membership_request_id, role=None):
        """Modify a membership request."""
        if not current_user.is_authenticated:
            abort(404)
        request = MembershipRequest.query.get(membership_request_id)
        community_admins = [admin.user.id for admin in
                            CommunityMember.get_admins(request.comm_id)]
        if not (int(current_user.get_id()) in community_admins and
                request.is_invite):
            abort(404)
        request.role = role
        db.session.commit()
        return 'Succesfully modified invitaion.', 200

    def delete(self, membership_request_id):
        """Cancel(remove) a membership request."""
        if not current_user.is_authenticated:
            abort(404)
        user_id = int(current_user.get_id())
        request = MembershipRequest.query.get(membership_request_id)
        if not (current_user.email == request.email and not request.is_invite):
            community_admins = [admin.user.id for admin in
                                CommunityMember.get_admins(request.comm_id)]
            if not (user_id in community_admins and request.is_invite):
                abort(404)
        MembershipRequestAPI.decline_or_cancel_invitation(request.id)

        db.session.commit()
        return 'Succesfully cancelled invitation.', 204


ui_blueprint = Blueprint(
    'invenio_communities_members',
    __name__,
    template_folder='../templates',
)


@ui_blueprint.route('/communities/<{0}:pid_value>/members'.format(
            'pid(comid,record_class="invenio_communities.api:Community",'
            'object_type="com")'))
@pass_community_function
def members(community, pid):
    """Members of a community."""
    return render_template(
        'invenio_communities/members.html', community=community, pid=pid)



@ui_blueprint.route('/communities/members/requests/<membership_request_id>')
def requests(membership_request_id):
    """Requests of communities."""
    return render_template('invenio_communities/request.html')
