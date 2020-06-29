# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort, jsonify, render_template, request
from flask.views import MethodView
from flask_login import current_user, login_required
from invenio_db import db
from invenio_accounts.models import User
from webargs import fields, validate

from invenio_communities.records.api import CommunityRecordsCollection

from ..utils import comid_url_converter, send_invitation_email
from ..views import pass_community, use_kwargs
from .api import CommunityMember, CommunityMemberRequest
from .errors import CommunityMemberAlreadyExists
from .models import COMMUNITY_MEMBER_MATCHES
from ..token import MembershipTokenSerializer
# TODO: Plan
# 1. Define REST API + payload/params/responses/codes
# 2. Implement REST API
# Checkpoint end of week
# 3. Review UI views (mockups/existing)
# 4. Implement views in React
# 5. Integrate/deploy
# Checkpoint end of sprint

api_blueprint = Blueprint(
        'invenio_communities_members',
        __name__,
        template_folder="../templates",
    )

class ListResource(MethodView):
    """Resource for creating, listing and removing community memberships."""

    post_args = {
        'role': fields.Raw(
            location='json',
            required=False,
            # TODO: Use enum here for the validation
            validate=[validate.OneOf(['member', 'admin', 'curator'])]
        ),
        'email': fields.Email(
            location='json',
            required=False
        ),
        'comment': fields.Raw(
            location='json',
            required=False
        )

    }

    @use_kwargs(post_args)
    @pass_community
    @login_required
    def post(self, comid=None, community=None, email=None, role=None,
             comment=None, **kwargs):
        """Join a community or invite a user to it."""
        request_user = User.query.get(int(current_user.get_id()))
        role = COMMUNITY_MEMBER_MATCHES[role] if role else 'M'
        # TODO add a comment in the codeflow for the request
        mem_req = CommunityMemberRequest.create(owner=request_user)
        # TODO: check if the user comparison here works
        if community.members.is_admin(request_user):
            # invitation
            if not email:
                # TODO: make bad request
                abort(404, 'Email is a required field.')
            try:
                # TODO: Use enums for the status and role
                comm_mem = community.members.add(
                    mem_req, status='P', role=role, invitation_id=email)
            # TODO: avoid exceptions
            except CommunityMemberAlreadyExists:
                abort(400, 'This is an already existing relationship.')
        else:
            # request to join
            if email:
                abort(403, 'You need to be a community administrator to '
                           'invite members to this community')
            try:
                comm_mem = community.members.add(
                    mem_req, status='P', user=request_user)
            # TODO: avoid exceptions
            except CommunityMemberAlreadyExists:
                abort(400, 'This is an already existing relationship.')

        if comment:
            mem_req.add_comment(request_user.id, comment)

        mts = MembershipTokenSerializer()
        inv_id = comm_mem.invitation_id
        token = mts.create_token(inv_id)

        #send_invitation_email(mem_req, email, community, token)

        db.session.commit()
        return comm_mem.as_dict(), 201

    get_args = {
        'status': fields.List(fields.Raw(
            location='querystring',
            required=False
        )
        ),
        'include_requests': fields.Boolean(
            location='querystring',
            required=False
        ),
        'role': fields.List(fields.Raw(
            location='querystring',
            required=False
        )
        ),
        'size': fields.Raw(
            location='querystring',
            required=False
        ),
        'page': fields.Raw(
            location='querystring',
            required=False
        ),
    }

    @use_kwargs(get_args)
    @pass_community
    @login_required
    def get(self, comid=None, community=None, status=None,
            include_requests=False, role=None, size=20, page=0):
        """List the community members."""
        request_user = User.query.get(int(current_user.get_id()))
        if not community.members.is_member(request_user):
            abort(404)
        if include_requests and not community.members.is_admin(request_user):
            abort(404)
        comm_members = community.members
        if status:
            comm_members = comm_members.filter(status=status)
        comm_members = comm_members.paginate(page=page, size=size)
        community_members_json = comm_members.as_dict(
            include_requests=include_requests)
        return jsonify(community_members_json), 200

    @pass_community
    @login_required
    def delete(self, comid=None, community=None, membership_id=None):
        """Remove a member from a community."""
        # TODO: maybe make this into a decorator?
        request_user = int(current_user.get_id())
        if request_user not in community.members.filter(role='A'):
            abort(404)
        community_member = CommunityMember.get_by_id(
            membership_id).delete()
        db.session.commit()
        return 'Succesfully removed', 204

"""
# Invite member via email
POST /api/communities/biosyslit/requests/members
{
    "email": "marcus@plazi.org",
    "role": "A",
    "comment": "Hi there",
}

{
    "id": "CM-1",
    "request_id": "CM-1-R",
}

GET /community/biosyslit/requests/members/CM-1?token=...

# Marcus' actions
    # To accept
    POST /api/communities/biosyslit/requests/members/CM-1/accept
    # To reject
    POST /api/communities/biosyslit/requests/members/CM-1/reject

# Donat's actions
    # Delete/cancel request
    GET /api/communities/biosyslit/requests/members?status=pending
    DELETE /api/communities/biosyslit/requests/members/CM-1
    DELETE /api/communities/biosyslit/members/CM-1

# After Marcus accepts the invitation
GET /api/communities/biosyslit/requests/members (comm_member.request) Admin
GET /api/communities/biosyslit/members?include_requests& status='Pending' (comm_member) Member


# Request to join community
POST /api/communities/biosyslit/requests/members
{
    "comment": "Hi there, Guido here",
}

{
    "id": "CM-2",
    "request_id": "CM-2-R",
}

GET /community/biosyslit/requests/members/CM-2?token=...

# Donat's actions
    # To accept
    POST /api/communities/biosyslit/requests/members/CM-2/accept
    # To reject
    POST /api/communities/biosyslit/requests/members/CM-2/reject

# Guido's actions
    # Delete/cancel request
    GET /api/communities/biosyslit/requests/members?status=pending
    DELETE /api/communities/biosyslit/requests/members/CM-2
    DELETE /api/communities/biosyslit/members/CM-2

# After Donat accepts the request
GET /api/communities/biosyslit/requests/members (comm_member.request) Admin
GET /api/communities/biosyslit/members?include_requests& status='Pending' (comm_member) Member

"""

class CommunityRequestList(MethodView):

    @pass_community
    @login_required
    def get(self, comid=None, community=None):
        """List the community members requests."""
        request_user = User.query.get(int(current_user.get_id()))
        # TODO: check when making the UI
        if request_user in community.members.filter(role='A'):
            community_members_json = community.members.as_dict(
                include_requests=True)
        else:
            abort(404)
        return jsonify(ui_members), 200


class CommunityRequestsResource(MethodView):
    """Resource to list community membership requests."""

    # TODO: this could be included in the other get with more parameters
    @pass_community
    @login_required
    def get(self, comid=None, community=None, outgoing_only=False,
            incoming_only=False, page_size=20, page=0):
        # TODO: pagination
        """List all the community members."""
        request_user = User.query.get(int(current_user.get_id()))
        if request_user not in community.members.filter(role='A'):
            abort(404)
        community_requests_json = community.members.filter(
            status='P').as_dict(include_requests=True)
        return jsonify(community_requests_json), 200


class MembershipRequestResource(MethodView):
    """Resource to view and handle membership requests."""

    @pass_community
    @login_required
    def get(self, comid=None, community=None, membership_id=None):
        """Get the information for a membership request."""
        request_user = User.query.get(int(current_user.get_id()))
        community_member = CommunityMember.get_by_id(
            membership_id)
        if not community.members.is_admin(request_user) and \
                request_user.id != community_member.user.id:
            abort(404)
        response_object = community_member.as_dict(include_requests=True)
        # response_object = {}
        # response_object['community_name'] = community.json['title']
        # response_object['community_id'] = community.json['id']
        # response_object['role'] = str(member_request.role.title)
        return jsonify(response_object), 200

    put_args = {
        'role': fields.Raw(
            location='json',
            required=True,
            validate=[validate.OneOf(['M', 'A', 'C'])]
        )
    }

    @use_kwargs(put_args)
    @pass_community
    @login_required
    def put(self, comid=None, community=None, membership_id=None,
            role=None):
        """Modify a membership request."""
        request_user = User.query.get(int(current_user.get_id()))
        community_member = CommunityMember.get_by_id(
            membership_id)
        if not community.members.is_admin(request_user):
            abort(404)

        community_member.role = role
        db.session.commit()
        # return jsonify(community_member.as_dict()), 200
        return 'Succesfully modified invitation.', 200

    del_args = {
        'token': fields.Raw(
            location='json',
            required=False,
        )
    }

    @use_kwargs(del_args)
    @pass_community
    @login_required
    def delete(self, comid=None, community=None, membership_id=None, token=None):
        """Cancel (remove) a membership request."""
        # TODO transfer into delete Member endpoint
        request_user = User.query.get(int(current_user.get_id()))
        community_member = CommunityMember.get_by_id(
            membership_id)
        if not community_member:
            abort(404)
        if community_member.request.is_closed:
            abort(404)
        if community_member.request.is_invite:
            if request_user.id != community_member.request.user_id:
               abort(404)
        elif not community.members.is_admin(request_user):
            abort(404)

        community_member.delete()
        db.session.commit()
        return 'Succesfully cancelled invitation.', 204

class MembershipRequestHandlingResource(MethodView):
    """Resource to view and handle membership requests."""

    post_args = {
        'role': fields.Raw(
            location='json',
            required=False,
            validate=[validate.OneOf(['member', 'admin', 'curator'])]
        ),
        'token': fields.Raw(
            location='json',
            required=False,
        ),
        'message': fields.Raw(
            location='json',
            required=False,
        )
    }

    @use_kwargs(post_args)
    @pass_community
    @login_required
    def post(self, comid=None, community=None, membership_id=None, action=None,
             role=None, message=None, token=None):
        """Add a comment."""
        request_user = User.query.get(int(current_user.get_id()))

        #
        # Controller
        #
        community_member = CommunityMember.get_by_id(
            membership_id)

        if community_member.request.is_closed and \
                action != 'comment':
            abort(404)

        mts = MembershipTokenSerializer()
        inv_id = community_member.invitation_id

        if community_member.request.is_invite:
           if not token or not mts.validate_token(
                token, expected_value=inv_id):
               abort(404)
        elif not community.members.is_admin(request_user):
            abort(404)

        if action == 'accept':
            community_member.status = 'A'
            if community_member.request.is_invite:
                community_member.user_id = request_user.id
            if role and community.members.is_admin(request_user):
                community_member.role = COMMUNITY_MEMBER_MATCHES[role]
            else:
                abort(400)
            community_member.request.close_request()
            # TODO: this state feels awkward
        elif action == 'reject':
            community_member.status = 'R'
            community_member.request.close_request()
        if message:
            community_member.request.add_comment(request_user.id, message)
        community_member.request.commit()
        db.session.commit()
        # TODO response?
        return jsonify(community_member.as_dict()), 200


api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>/members'.format(pid=comid_url_converter),
    view_func=ListResource.as_view('community_members_api'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>/requests/members'.format(pid=comid_url_converter),
    view_func=CommunityRequestList.as_view('community_members_requests_api'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/members/requests/<membership_id>/<any({actions}):action>'.format(
        pid=comid_url_converter,
        actions=','.join(['accept', 'reject', 'comment'])),
    view_func=MembershipRequestHandlingResource.as_view(
        'community_requests_handling_api'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/members/requests/<membership_id>'.format(pid=comid_url_converter),
    view_func=CommunityRequestsResource.as_view(
        'community_requests_management_api'),
)

# TODO: the community pid is not needed in these endpoints
api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>/members/requests/<membership_id>'.format(
        pid=comid_url_converter),
    view_func=MembershipRequestResource.as_view(
        'community_requests_api'),
)


ui_blueprint = Blueprint(
    'invenio_communities_members',
    __name__,
    template_folder='../templates',
)


@login_required
@ui_blueprint.route(
    '/communities/<{}:pid_value>/members'.format(comid_url_converter))
@pass_community
def members(comid=None, community=None):
    """Members of a community."""
    pending_records = \
        len(community.members.filter(status='P'))

    return render_template(
        'invenio_communities/members.html',
        community=community,
        comid=comid,
        pending_records=pending_records
    )


@login_required
@ui_blueprint.route('/communities/members/requests/<membership_id>')
def requests(membership_id):
    """Requests of communities."""
    return render_template('invenio_communities/request.html')
