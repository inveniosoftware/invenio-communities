# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions for records integration."""

import uuid
from functools import wraps

from flask import Blueprint, abort, jsonify, render_template, request, url_for
from flask.views import MethodView
from flask_login import current_user, login_required
from invenio_accounts.models import User
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_pidstore.errors import PIDDoesNotExistError
from sqlalchemy.exc import SQLAlchemyError
from webargs import fields

from invenio_communities.records.api import CommunityInclusionRequest, \
    CommunityRecord, CommunityRecordsCollection, Record, \
    RecordCommunitiesCollection

from ..utils import comid_url_converter, send_inclusion_email
from ..views import pass_community, use_kwargs
from .errors import CommunityRecordAlreadyExists
from .permissions import CommunityRecordPermissionPolicy, is_permitted_action

#
# UI views
#
ui_blueprint = Blueprint(
    'invenio_communities_records',
    __name__,
    template_folder='../templates',
)


def pass_record(func=None):
    """Decorator to retrieve community record."""
    @wraps(func)
    def inner(*args, record_pid=None, **kwargs):
        try:
            record_pid, record = CommunityRecord.record_cls.resolve(record_pid)
        except PIDDoesNotExistError:
            abort(404)
        return func(*args, record_pid=record_pid, record=record, **kwargs)
    return inner


def pass_community_record(func=None):
    """Decorator to retrieve community inclusion."""
    @wraps(func)
    def inner(*args, **kwargs):
        del kwargs['community_record_id']
        community_record_id = request.view_args['community_record_id']
        community_record = CommunityRecord.get_record(community_record_id)
        if community_record is None:
            abort(404)
        return func(*args, community_record=community_record, **kwargs)
    return inner


def community_permission(
        action=None,
        error_message='You are missing the permissions to '
                      'access this information.',
        error_code=403):
    """Wrapper to apply a permission check on a view."""
    def wrapper_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CommunityRecordPermissionPolicy(action=action, **kwargs):
                abort(error_code, error_message)
            return func(*args, **kwargs)
        return wrapper
    return wrapper_function


@ui_blueprint.route(
    '/communities/<{}:pid_value>/curate'.format(comid_url_converter))
@pass_community
@login_required
@community_permission('list_community_inclusions')
def curation(comid=None, community=None):
    """Curate page for community record inclusions."""
    pending_records = \
        len(CommunityRecordsCollection(community).filter({'status': 'P'}))

    return render_template(
        'invenio_communities/curation.html',
        community=community,
        comid=comid,
        pending_records=pending_records
    )


#
# REST API views
#
api_blueprint = Blueprint(
    'invenio_communities_records',
    __name__,
    template_folder='../templates',
)


def dump_community_record_request_links(community_record):
    if community_record.request.is_closed:
        actions = ['comment']
    else:
        actions = ['comment', 'accept', 'reject']
    links = {
        "self": url_for(
            'invenio_communities_records.community_records_item',
            pid_value=community_record.community.pid.pid_value,
            community_record_id=community_record.id
        )
    }
    for action in actions:
        links[action] = url_for(
            'invenio_communities_records.community_records_item_actions',
            pid_value=community_record.community.pid.pid_value,
            community_record_id=community_record.id,
            action=action
        )
    return links


class ListResource(MethodView):
    """Resource for listing and creating inclusion requests."""

    post_args = {
        'record_pid': fields.String(
            location='json',
            required=True,
        ),
        'message': fields.String(
            location='json',
            required=False,
        ),
        'auto_accept': fields.Boolean(
            location='json',
            required=False,
        )
    }

    @pass_community
    @login_required
    @community_permission('list_community_inclusions')
    def get(self, comid=None, community=None):
        """List the community records requests."""
        json_response = community.records.as_dict()
        return jsonify(json_response), 200

    @use_kwargs(post_args)
    @pass_community
    @pass_record
    @login_required
    @community_permission('create_community_inclusion')
    def post(self, comid=None, community=None, record=None, record_pid=None,
             message=None, auto_accept=False, **kwargs):
        """Join a community or invite a user record to it."""
        #
        # View - context parsing/building
        #
        user = current_user

        #
        # Controller
        #
        request = CommunityInclusionRequest.create(user, id_=uuid.uuid4())
        if message:
            request.add_comment(user, message)
        try:
            com_rec = CommunityRecord.create(
                record, record_pid, community, request)
        except CommunityRecordAlreadyExists:
            abort(400, 'Community-record relationship already exists.')
        com_rec.status = com_rec.Status.PENDING

        if user.id in record['_owners']:
            # if user is also a community owner and auto-accepted:
            if auto_accept and community['created_by'] == user.id:
                request['state'] = request.State['CLOSED']
                com_rec.status = com_rec.Status.ACCEPTED
                request['inclusion_type'] = 'auto-accepted'
            else:
                request['inclusion_type'] = 'request'
        else:
            request['inclusion_type'] = 'invite'
        db.session.commit()

        if request['inclusion_type'] == 'invite':
            recipient_emails = [
                User.query.get(owner_id).email for owner_id in record['_owners']]
        elif request['inclusion_type'] == 'request':
            recipient_emails = [User.query.get(community['created_by']).email]
        RecordIndexer().index_by_id(record.id)
        send_inclusion_email(com_rec, recipient_emails)

        json_response = request.as_dict()
        json_response['links'] = dump_community_record_request_links(com_rec)

        #
        # View - serialize response
        #
        return jsonify(json_response), 201


class ItemResource(MethodView):
    """Community inclusion request item endpoint."""

    @pass_community
    @pass_community_record
    @login_required
    @community_permission('get_community_inclusion')
    def get(self, comid=None, community=None, inclusion=None):
        """Get the inclusion request."""
        json_response = inclusion.as_dict(include_requests=True)
        return jsonify(json_response), 200

    @pass_community
    @pass_community_record
    @login_required
    @community_permission('delete_community_inclusion')
    def delete(self, comid=None, community=None, inclusion=None):
        """Delete the community record request."""
        community_record = request.community_record
        community_record.delete()
        request.delete()
        db.session.commit()
        return 204


# TODO: move things around
class ItemActionsResource(MethodView):
    """Perform actions on inclusion requests."""

    post_args = {
        'message': fields.String(
            location='json',
            required=False,
        )
    }

    @use_kwargs(post_args)
    @pass_community
    @pass_community_record
    @login_required
    def post(self, comid=None, community=None, community_record=None,
             action=None, message=None, **kwargs):
        """Handle a community record request."""
        #
        # View - context parsing/building
        #
        inclusion_request = community_record.request
        if action == 'comment':
            if not is_permitted_action(
                    'comment_community_inclusion',
                    community_record=community_record, community=community):
                abort(404)
            if not message:
                abort(400, 'Missing comment message.')
        elif not is_permitted_action(
                'handle_community_inclusion',
                community_record=community_record, community=community):
            abort(404)
        elif action == 'accept':
            community_record.status = community_record.Status.ACCEPTED
            inclusion_request.state = 'closed'
        elif action == 'reject':
            community_record.status = community_record.Status.REJECTED
            inclusion_request.state = 'closed'
        else:
            abort(400, 'Invalid action')
        if message:
            inclusion_request.add_comment(current_user, message)
        db.session.commit()

        # Notify request owners and receivers
        # TODO: implement mail sending
        # send_request_emails(request)

        # Index record with new inclusion request info
        RecordIndexer().index_by_id(community_record.record.id)

        #
        # View - serialize response
        #

        return jsonify(community_record.as_dict()), 201


api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/inclusion/requests'.format(pid=comid_url_converter),
    view_func=ListResource.as_view('community_records_list'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/inclusion/requests/<uuid:community_record_id>'.format(
        pid=comid_url_converter),
    view_func=ItemResource.as_view('community_records_item'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/inclusion/requests/<uuid:community_record_id>'
    '/<any({actions}):action>'.format(
        pid=comid_url_converter,
        actions=','.join(['accept', 'reject', 'comment'])),
    view_func=ItemActionsResource.as_view('community_records_item_actions'),
)
