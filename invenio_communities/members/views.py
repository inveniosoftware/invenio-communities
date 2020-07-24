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
from .models import CommunityMemberRole, CommunityMemberStatus
from .errors import CommunityMemberAlreadyExists
from ..token import MembershipTokenSerializer


api_blueprint = Blueprint(
        'invenio_communities_members',
        __name__,
        template_folder="../templates",
    )


member_role_validator = validate.OneOf(
    [c.name.lower() for c in CommunityMemberRole])

member_status_validator = validate.OneOf(
    [c.name.lower() for c in CommunityMemberStatus])


class ListResource(MethodView):
    """Resource for creating, listing and removing community memberships."""

    post_args = {
        'role': fields.Str(
            location='json',
            required=False,
            validate=member_role_validator,
        ),
        'email': fields.Email(
            location='json',
            required=False,
        ),
        'comment': fields.Str(
            location='json',
            required=False,
        ),
    }

    @use_kwargs(post_args)
    @pass_community
    @login_required
    def post(self, comid=None, community=None, email=None, role=None,
             comment=None, **kwargs):
        """Join a community or invite a user to it."""
        request_user = User.query.get(int(current_user.get_id()))
        # TODO: see if there's a marshmallow field for this
        if role:
            role = CommunityMemberRole.from_str(role)
        # TODO add a comment in the codeflow for the request
        mem_req = CommunityMemberRequest.create(owner=request_user)
        # TODO: check if the user comparison here works
        if request_user in community.members.filter(
                role=CommunityMemberRole.ADMIN):
            # invitation
            if not email:
                # TODO: make bad request
                abort(404, 'Email is a required field.')
            try:
                comm_mem = community.members.add(
                    mem_req,
                    status=CommunityMemberStatus.PENDING,
                    role=role,
                    invitation_id=email,
                )
            # TODO: avoid exceptions
            except CommunityMemberAlreadyExists:
                abort(400, 'This is an already existing relationship.')
        else:
            # request to join
            if email:
                abort(403, 'You need to be a community administrator to '
                           'invite members to this community')
            if role:
                abort(403, 'Selecting a role is not possible when requesting'
                           ' to join a community')
            try:
                comm_mem = community.members.add(
                    mem_req,
                    status=CommunityMemberStatus.PENDING,
                    user=request_user
                )
            # TODO: avoid exceptions
            except CommunityMemberAlreadyExists:
                abort(400, 'This is an already existing relationship.')

        if comment:
            mem_req.add_comment(request_user.id, comment)

        if email:
            mts = MembershipTokenSerializer()
            inv_id = comm_mem.invitation_id
            token = mts.create_token(inv_id)
            send_invitation_email(comm_mem, [email], community, token)
        else:
            emails = []
            admins = community.members.filter(
                role=CommunityMemberRole.ADMIN,
                status=CommunityMemberStatus.ACCEPTED)
            for admin in admins:
                emails.append(admin.user.email)
                send_invitation_email(comm_mem, emails, community)

        db.session.commit()
        return comm_mem.as_dict(), 201

    get_args = {
        #TODO make list when we manage to integrate the in operator
        'status': fields.Str(
            location='querystring',
            required=False,
            validate=member_status_validator
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
        'include_requests': fields.Bool(
            location='querystring',
            required=False
        ),
    }

    @use_kwargs(get_args)
    @pass_community
    @login_required
    def get(self, comid=None, community=None,
            status='accepted', role=None, page=1, size=20,
            include_requests=False):
        """List the community members."""
        user_id = int(current_user.get_id())
        if user_id not in community.members.filter(
                status=CommunityMemberStatus.ACCEPTED):
            abort(404)
        status = CommunityMemberStatus.from_str(status)
        if status != CommunityMemberStatus.ACCEPTED and user_id not in \
                community.members.filter(
                    role=CommunityMemberRole.ADMIN):
            abort(403, 'Only Admin members can see this information')

        members = community.members
        if status:
            members = members.filter(status=status)
        if role:
            members = members.filter(role=role)
        member_page = members.paginate(page=page, size=size)
        return members.as_dict(
            include_requests=include_requests, result_iterator=member_page), 200


class CommunityRequestList(MethodView):

    @pass_community
    @login_required
    def get(self, comid=None, community=None):
        """List the community members requests."""
        user_id = int(current_user.get_id())
        # TODO: check when making the UI
        if user_id in community.members.filter(
                role=CommunityMemberRole.ADMIN,
                status=CommunityMemberStatus.ACCEPTED):
            community_members_json = community.members.as_dict(
                include_requests=True)
        else:
            abort(404)
        return jsonify(community_members_json), 200

class MembershipRequestResource(MethodView):
    """Resource to view and handle membership requests."""

    @pass_community
    @login_required
    def get(self, comid=None, community=None, membership_id=None):
        """Get the information for a membership request."""
        user_id = int(current_user.get_id())
        community_member = CommunityMember.get_by_id(
            membership_id)
        if user_id not in community.members.filter(
                role=CommunityMemberRole.ADMIN) \
                and user_id.id != community_member.user.id:
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
            validate=member_role_validator,
        )
    }

    @use_kwargs(put_args)
    @pass_community
    @login_required
    def put(self, comid=None, community=None, membership_id=None,
            role=None):
        """Modify a membership role."""
        user_id = int(current_user.get_id())
        community_member = CommunityMember.get_by_id(
            membership_id)
        if community_member is None:
            abort(404)
        if user_id not in community.members.filter(
                role=CommunityMemberRole.ADMIN):
            abort(404)

        community_member.role = CommunityMemberRole.from_str(role)
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
    def delete(self, comid=None, community=None, membership_id=None):
        """Cancel (remove) a membership request."""
        # TODO transfer into delete Member endpoint
        # TODO dont allow last admin to leave
        user_id = int(current_user.get_id())
        community_member = CommunityMember.get_by_id(
            membership_id)
        if community_member is None:
            abort(404)
        if not community_member.request.is_closed:
            if community_member.request.is_invite:
                if user_id.id != community_member.request.user_id:
                    abort(404)
            elif user_id not in community.members.filter(
                    role=CommunityMemberRole.ADMIN):
                abort(404)
        else:
            if user_id not in community.members.filter(
                    role=CommunityMemberRole.ADMIN) or \
                    user_id != community_member.user_id:
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
            validate=member_role_validator,
        ),
        'token': fields.Raw(
            location='json',
            required=False,
        ),
        'comment': fields.Raw(
            location='json',
            required=False,
        )
    }

    @use_kwargs(post_args)
    @pass_community
    @login_required
    def post(self, comid=None, community=None, membership_id=None, action=None,
             role=None, comment=None, token=None):
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
        elif request_user not in community.members.filter(
                role=CommunityMemberRole.ADMIN):
            abort(404)

        if action == 'accept':
            community_member.status = CommunityMemberStatus.ACCEPTED
            if community_member.invitation_id:
                community_member.invitation_id = 'Cleaned'
            if community_member.request.is_invite:
                community_member.user_id = request_user.id
            if role and request_user in community.members.filter(
                    role=CommunityMemberRole.ADMIN):
                community_member.role = CommunityMemberRole.from_str(role)
            else:
                abort(400)
            community_member.request.close_request()
            # TODO: this state feels awkward
        elif action == 'reject':
            #TODO check if the invitation_id is properly cleaned up
            #TODO we need a value in the invitation_id for the history of the reqeusts direction
            if community_member.invitation_id:
                community_member.invitation_id = 'Cleaned'
            community_member.status = CommunityMemberStatus.REJECTED
            community_member.request.close_request()
        if comment:
            community_member.request.add_comment(request_user.id, comment)
        community_member.request.commit()
        db.session.commit()
        # TODO response?
        return jsonify(community_member.as_dict()), 200

    get_args = {
        'token': fields.Raw(
            location='query',
            required=False,
        )}

    @use_kwargs(get_args)
    @pass_community
    @login_required
    def get(self, comid=None, community=None, membership_id=None, token=None):
        request_user = User.query.get(int(current_user.get_id()))
        #
        # Controller
        #
        community_member = CommunityMember.get_by_id(
            membership_id)

        mts = MembershipTokenSerializer()
        inv_id = community_member.invitation_id

        if request_user not in community.members.filter(
                role=CommunityMemberRole.ADMIN) and \
            (not token or not mts.validate_token(
                    token, expected_value=inv_id)):
            abort(404)

        return jsonify(community_member.as_dict(include_requests=True)), 200


api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>/members'.format(pid=comid_url_converter),
    view_func=ListResource.as_view('community_members_api'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>/members/requests'.format(pid=comid_url_converter),
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


@ui_blueprint.route(
    '/communities/<{}:pid_value>/members'.format(comid_url_converter))
@pass_community
@login_required
def members(comid=None, community=None):
    """Members of a community."""
    pending_records = \
        len(community.members.filter(status=CommunityMemberStatus.PENDING))
    community_member_obj = community.members.get_user_membership(
        int(current_user.get_id()),
        status=CommunityMemberStatus.ACCEPTED
    )
    if community_member_obj is not None:
        community_member = community_member_obj.as_dict()
    else:
        community_member = {}
    return render_template(
        'invenio_communities/members.html',
        community=community,
        comid=comid,
        pending_records=pending_records,
        community_member=community_member
    )


@ui_blueprint.route(
    '/communities/<{}:pid_value>/members/requests/<membership_id>'.format(
        comid_url_converter))
@pass_community
@login_required
def requests(comid=None, community=None, membership_id=None):
    """Requests of communities."""
    token = request.args.get('token', '')
    community_member = CommunityMember.get_by_id(membership_id)
    if community_member is None:
        abort(404)
    mts = MembershipTokenSerializer()
    inv_id = community_member.invitation_id

    if not community_member.request.is_invite:
        abort(404)
    if not token or not mts.validate_token(
            token, expected_value=inv_id):
        abort(404)
    return render_template(
        'invenio_communities/request.html',
        comid=comid,
        community=community,
        membership=community_member.as_dict(include_requests=True),
        token=token
    )
