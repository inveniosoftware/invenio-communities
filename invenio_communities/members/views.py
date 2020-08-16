# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from functools import partial, wraps

from flask import Blueprint, abort, jsonify, render_template, request
from flask.views import MethodView
from flask_login import current_user, login_required
from invenio_accounts.models import User
from invenio_db import db
from webargs import fields, validate

from invenio_communities.records.api import CommunityRecordsCollection

from ..token import MembershipTokenSerializer
from ..utils import comid_url_converter, send_invitation_email
from ..views import pass_community, use_kwargs
from .api import CommunityMember, CommunityMemberRequest
from .errors import CommunityMemberAlreadyExists
from .models import CommunityMemberRole, CommunityMemberStatus
from .permissions import CommunityMemberPermissionPolicy, is_permitted_action

api_blueprint = Blueprint(
        'invenio_communities_members',
        __name__,
        template_folder="../templates",
    )


def pass_membership(func=None, view_arg_name='membership_id'):
    """Decorator to retrieve community membership."""
    if func is None:
        return partial(pass_membership, view_arg_name=view_arg_name)

    @wraps(func)
    def inner(*args, **kwargs):
        del kwargs[view_arg_name]
        membership_id = request.view_args[view_arg_name]
        community_member = CommunityMember.get_by_id(membership_id)
        if community_member is None:
            abort(404)
        return func(*args, community_member=community_member, **kwargs)
    return inner


def community_permission(
        action=None,
        error_message='You are missing the permissions to'
                      'access this information.',
        error_code=403):
    """Wrapper to apply a permission check on a view."""
    def wrapper_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CommunityMemberPermissionPolicy(action=action, **kwargs):
                abort(error_code, error_message)
            return func(*args, **kwargs)
        return wrapper
    return wrapper_function


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
    @community_permission('create_membership')
    def post(self, comid=None, community=None, email=None, role=None,
             comment=None, **kwargs):
        """Join a community or invite a user to it."""
        request_user = User.query.get(int(current_user.get_id()))
        # TODO: see if there's a marshmallow field for this
        if role:
            role = CommunityMemberRole.from_str(role)
        mem_req = CommunityMemberRequest.create(owner=request_user)
        if request_user in community.members.filter(
                role=CommunityMemberRole.ADMIN,
                status=CommunityMemberStatus.ACCEPTED):
            # invitation
            if not email:
                abort(400, 'Email is a required field.')
            try:
                comm_mem = community.members.add(
                    mem_req,
                    status=CommunityMemberStatus.PENDING,
                    role=role,
                    invitation_id=email,
                )
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


class ListMembersResource(MethodView):
    """Resource for creating, listing and removing community memberships."""

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
        )
    }

    @use_kwargs(get_args)
    @pass_community
    @login_required
    def get(self, comid=None, community=None,
            status=None, role=None, page=1, size=20):
        """List the community members."""
        if not is_permitted_action(
            'list_{}_members'.format(status),
                comid=comid):
            abort(403, 'You are missing the permissions to'
                       'access this information.')
        status = CommunityMemberStatus.from_str(status)

        members = community.members
        members = members.filter(status=status)
        if status != 'accepted':
            include_requests = True
        else:
            include_requests = False
        if role:
            members = members.filter(role=role)
        member_page = members.paginate(page=page, size=size)
        return members.as_dict(
            include_requests=include_requests,
            result_iterator=member_page
            ), 200


class MembershipRequestResource(MethodView):
    """Resource to view and handle membership requests."""

    get_args = {
        'token': fields.Raw(
            location='query',
            required=False,
        )}

    @use_kwargs(get_args)
    @pass_community
    @pass_membership
    @login_required
    @community_permission('get_membership')
    def get(
            self, comid=None, community=None, token=None,
            community_member=None):
        """Get a membership along with it's request information."""
        mts = MembershipTokenSerializer()
        inv_id = community_member.invitation_id

        if community_member.request.is_invite \
            and (not token or not mts.validate_token(
                    token, expected_value=inv_id)):
            abort(404)
        # TODO links are currently missing.
        return jsonify(community_member.as_dict(include_requests=True)), 200

    put_args = {
        'role': fields.Raw(
            location='json',
            required=True,
            validate=member_role_validator,
        )
    }

    @use_kwargs(put_args)
    @pass_community
    @pass_membership
    @login_required
    @community_permission('modify_membership')
    def put(self, comid=None, community=None,
            role=None, community_member=None):
        """Modify a membership role."""
        community_admins = community.members.filter(
            role=CommunityMemberRole.ADMIN,
            status=CommunityMemberStatus.ACCEPTED)

        if len(community_admins) == 1 and \
                community_member.role == CommunityMemberRole.ADMIN:
            abort(400, 'Cannot remove last community Administrator.')

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
    @pass_membership
    @login_required
    @community_permission('delete_membership')
    def delete(self, comid=None, community=None, community_member=None):
        """Cancel (remove) a membership request."""
        # TODO dont allow last admin to leave
        community_admins = community.members.filter(
            role=CommunityMemberRole.ADMIN,
            status=CommunityMemberStatus.ACCEPTED)
        if len(community_admins) == 1 and \
                community_member.role == CommunityMemberRole.ADMIN:
            abort(400, 'Cannot remove last community Administrator.')

        community_member.delete()
        db.session.commit()
        return 'Succesfully removed membership.', 204


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
    @pass_membership
    @login_required
    @community_permission('handle_request')
    def post(self, comid=None, community=None, community_member=None,
             action=None, role=None, comment=None, token=None):
        """Add a comment."""
        request_user = User.query.get(int(current_user.get_id()))
        #
        # Controller
        #
        if community_member.request.is_closed and \
                action != 'comment':
            abort(400)

        mts = MembershipTokenSerializer()
        inv_id = community_member.invitation_id

        if community_member.request.is_invite:
            if not token or not mts.validate_token(
                    token, expected_value=inv_id):
                abort(404)

        if action == 'accept':
            community_member.status = CommunityMemberStatus.ACCEPTED
            if community_member.request.is_invite:
                community_member.user_id = request_user.id
            if community_member.invitation_id:
                community_member.invitation_id = None
            if role:
                if request_user in community.members.filter(
                        role=CommunityMemberRole.ADMIN,
                        status=CommunityMemberStatus.ACCEPTED):
                    community_member.role = CommunityMemberRole.from_str(role)
                else:
                    abort(400)
            community_member.request.close_request()
        elif action == 'reject':
            #TODO check if the invitation_id is properly cleaned up
            if community_member.invitation_id:
                community_member.invitation_id = None
            community_member.status = CommunityMemberStatus.REJECTED
            community_member.request.close_request()
        if comment:
            community_member.request.add_comment(request_user.id, comment)
        community_member.request.commit()
        db.session.commit()
        # TODO response?
        return jsonify(community_member.as_dict()), 200


api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>/members'.format(pid=comid_url_converter),
    view_func=ListResource.as_view('community_members_api'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>/members/<any({status}):status>'.format(
        pid=comid_url_converter,
        status=','.join(['accepted', 'rejected', 'pending'])),
    view_func=ListMembersResource.as_view('community_members_list_api'),
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
    community_member_obj = community.members.get_user_membership(
        int(current_user.get_id()),
        status=CommunityMemberStatus.ACCEPTED
    )
    if community_member_obj is not None:
        community_member = community_member_obj.as_dict()
        pending_records = \
            len(community.members.filter(status=CommunityMemberStatus.PENDING))

    else:
        community_member = {}
        pending_records = {}
    #TODO pending records should also check permissions
    #  before exposing this information
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
@pass_membership
@login_required
def requests(
        comid=None, community=None, community_member=None):
    """Requests of communities."""
    token = request.args.get('token', '')
    if not community_member.request.is_invite:
        abort(404)
    mts = MembershipTokenSerializer()
    inv_id = community_member.invitation_id

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
