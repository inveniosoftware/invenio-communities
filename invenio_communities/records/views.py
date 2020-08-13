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
from flask import Blueprint, abort, jsonify, render_template, request
from flask.views import MethodView
from flask_login import current_user, login_required
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from sqlalchemy.exc import SQLAlchemyError
from webargs import fields
from invenio_pidstore.errors import PIDDoesNotExistError

from invenio_communities.records.api import CommunityInclusionRequest, \
    CommunityRecord, CommunityRecordsCollection, Record, \
    RecordCommunitiesCollection

from ..utils import comid_url_converter
from ..views import pass_community, use_kwargs
from .errors import CommunityRecordAlreadyExists

#
# UI views
#
ui_blueprint = Blueprint(
    'invenio_communities_records',
    __name__,
    template_folder='../templates',
)
def pass_record(func=None):
    """Decorator to retrieve community membership."""
    def inner(*args, record_pid=None, **kwargs):
@login_required
@community_permission('can_list_community_inclusions')
    """Curate page for community record inclusions."""
            record_pid, record = CommunityRecord.record_cls.resolve(record_pid)
        except PIDDoesNotExistError:
            abort(404)
        return func(*args, record_pid=record_pid, record=record, **kwargs)
    return inner


def pass_request(func=None):
    """Decorator to retrieve community membership."""
    @wraps(func)
    def inner(*args, **kwargs):
        del kwargs['request_id']
        request_id = request.view_args['request_id']
        inclusion_request = CommunityInclusionRequest.get_record(request_id)
        if inclusion_request is None:
            abort(404)
        return func(*args, inclusion_request=inclusion_request, **kwargs)
    return inner


def community_permission(


@ui_blueprint.route(
    '/communities/<{}:pid_value>/curate'.format(comid_url_converter))
@login_required
@pass_community
def curation(comid=None, community=None):
    """Create a new community."""
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

    @pass_record
    def post(self, comid=None, community=None, record=None, record_pid=None,
class ListResource(MethodView):
        """Join a community or invite a user record to it."""

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
    def get(self, comid=None, community=None):
        """List the community records requests."""
        # TODO: check if user in community or record owner
        json_response = community.records.as_dict()
        return jsonify(json_response), 200

    @use_kwargs(post_args)
    @pass_community
    @login_required
    def post(self, comid=None, community=None, record_pid=None,
             message=None, auto_accept=False, **kwargs):
        """Join a community or invite a user to it."""
        if user.id in record['_owners']:
            # if user is also a community owner and auto-accepted:
            if auto_accept and community['created_by'] == user.id:
        #
        user = current_user

        #
        # Controller
                request['inclusion_type'] = 'auto-accepted'
        #
        # TODO: implement "__contains__" in members collection API
        # admin_ids = \
        #     [admin.user.id for admin in CommunityMember.get_admins(
                request['inclusion_type'] = 'request'
        # if int(current_user.get_id()) not in admin_ids:
        #     abort(404)

        # TODO: Consider also
            request['inclusion_type'] = 'invite'
        record_pid, record = CommunityRecord.record_cls.resolve(record_pid)
        request = CommunityInclusionRequest.create(user, id_=uuid.uuid4())
        if message:
            request.add_comment(user, message)
        try:
            com_rec = CommunityRecord.create(
                record, record_pid, community, request)
        except CommunityRecordAlreadyExists:
            abort(400, 'Community-record relationship already exists.')
        com_rec.status = com_rec.Status.PENDING

        # TODO: Check in community members instead of just creator
        # if CommunityMembersAPI.has_member(community, user):
        if community['created_by'] == user.id:
            if auto_accept:
                # TODO: define what the routing_key value should be
                # request.routing_key = ''
                # TODO: implement state as a "Request.state" property?
                request['state'] = request.State['CLOSED']
                com_rec.status = com_rec.Status.ACCEPTED
            else:
                # TODO: define what the routing_key value should be
                # TODO: don't use f-strings
    @pass_request
    def get(self, comid=None, community=None, inclusion_request=None):
                pass
        else:
        json_response = inclusion_request.as_dict()
            #     f'community:{community.pid.pid_value}:curators'
            pass
        db.session.commit()

    @pass_request
    def delete(self, comid=None, community=None, inclusion_request=None):
        # TODO: implement mail sending (e.g. via "routing_key")
        # send_request_emails(request)
        json_response = request.as_dict()
        json_response['links'] = request.dump_links(request, comid.pid_value)

        #
        # View - serialize response
        #
        # TODO: Use marshmallow to serialize
        return jsonify(json_response), 201


class ItemResource(MethodView):
    """Community inclusion request item endpoint."""

    @pass_community
    @login_required
    def get(self, comid=None, community=None, request_id=None):
        """Get the inclusion request."""
        # TODO: check if user in community or record owner
        request = CommunityInclusionRequest.get_record(request_id)
        json_response = request.as_dict()
        return jsonify(json_response), 200

    @pass_community
    @login_required
    def delete(self, comid=None, community=None, request_id=None):
    @pass_request
        """Delete the inclusion request."""
        # TODO: check if user in community or record owner
    def post(self, comid=None, community=None, inclusion_request=None,
             action=None, message=None, **kwargs):
            request = CommunityInclusionRequest.get_record(request_id)
        except SQLAlchemyError:
            abort(404, 'Record inclusion request not found.')
        community_record = request.community_record
        community_record = inclusion_request.community_record
            required=False,
            if not is_permitted_action(
        )
    }

    @use_kwargs(post_args)
    @pass_community
    @login_required
    # TODO: Swap `request_id` with `CommunityRecord.id` (instead of `Request.id`)
    def post(self, comid=None, community=None, request_id=None, action=None,
             message=None, **kwargs):
        """Handle a community record request."""
        #
        # View - context parsing/building
        #
        user = current_user

        #
            # inclusion_request.routing_key = ''
        #
            inclusion_request['state'] = inclusion_request.STATES['CLOSED']
        #     [admin.user.id for admin in CommunityMember.get_admins(
        #         community.id)]
        # if int(current_user.get_id()) not in admin_ids:
            # inclusion_request.routing_key = ''
            inclusion_request['state'] = inclusion_request.STATES['CLOSED']
        request = CommunityInclusionRequest.get_record(request_id)
        community_record = request.community_record
            abort(400, 'Invalid action')
            if not message:
            inclusion_request.add_comment(current_user, message)
                abort(400, 'Missing comment message.')
        elif action == 'accept':
            community_record.status = community_record.Status.ACCEPTED
            # TODO: figure out "routing_key"
            # request.routing_key = ''
            # TODO: use ".state" property setter/getter
            request['state'] = request.State['CLOSED']
        elif action == 'reject':
            community_record.status = community_record.Status.REJECTED
            # TODO: figure out "routing_key"
            # request.routing_key = ''
            request['state'] = request.State['CLOSED']
        else:
            # TODO: no appropriate action error
        # TODO: Use marshmallow to serialize
        if message:
            request.add_comment(user, message)
        db.session.commit()

        # Notify request owners and receivers
        # TODO: implement mail sending
        # send_request_emails(request)

        # Index record with new inclusion request info
        # TODO: Implement indexer receiver to include community info in record
        # TODO: check if it's always needed to index the record
        RecordIndexer().index_by_id(community_record.record.id)

        #
        # View - serialize response
        #
        # TODO: User marshmallow to serialize
        return jsonify(community_record.as_dict()), 201


api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/requests/inclusion'.format(pid=comid_url_converter),
    view_func=ListResource.as_view('requests_list'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/requests/inclusion/<uuid:request_id>'.format(pid=comid_url_converter),
    view_func=ItemResource.as_view('requests_item'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/requests/inclusion/<uuid:request_id>'
    '/<any({actions}):action>'.format(
        pid=comid_url_converter,
        actions=','.join(['accept', 'reject', 'comment'])),
    view_func=ItemActionsResource.as_view('requests_item_actions'),
)
