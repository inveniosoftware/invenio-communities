# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions for records collections."""

import copy
from functools import wraps

from flask import Blueprint, abort, jsonify, render_template, url_for
from flask.views import MethodView
from flask_login import login_required
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from sqlalchemy.exc import SQLAlchemyError
from webargs import fields

from invenio_communities.records.api import CommunityInclusionRequest, \
    CommunityRecord

from ...utils import comid_url_converter
from ...views import pass_community, use_kwargs
from .permissions import CommunityCollectionsPermissionPolicy


def community_permission(
        action=None,
        error_message='You are missing the permissions to '
                      'access this information.',
        error_code=403):
    """Wrapper to apply a permission check on a view."""
    def wrapper_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CommunityCollectionsPermissionPolicy(action=action, **kwargs):
                abort(error_code, error_message)
            return func(*args, **kwargs)
        return wrapper
    return wrapper_function


#
# UI views
#
ui_blueprint = Blueprint(
    'invenio_communities_collections',
    __name__,
    template_folder='../../templates',
)


# Collections management settings page

"""
Widget in the record page
Search filtering
Bulk in community
"""

#
# REST API views
#
api_blueprint = Blueprint(
    'invenio_communities_collections',
    __name__,
)


class ListResource(MethodView):
    """Resource for listing and creating collections."""

    post_args = {
        'id': fields.String(
            location='json',
            required=True,
        ),
        'title': fields.String(
            location='json',
            required=True,
        ),
        'description': fields.String(
            location='json',
            required=False,
        )
    }

    @pass_community
    @community_permission('list_collections')
    def get(self, comid=None, community=None):
        """List the community collections."""
        return jsonify(community.collections.as_dict())

    @use_kwargs(post_args)
    @pass_community
    @login_required
    @community_permission('create_collection')
    def post(self, comid=None, community=None, id=None, title=None,
             description=None, **kwargs):
        """Create a community collection."""
        if id in community.collections:
            abort(400, 'There is already a collection with the ID "{}" in the community'.format(id))

        collection = community.collections.add(
            id, title=title, description=description)
        db.session.commit()
        json_response = copy.deepcopy(collection)
        json_response['links'] = {
            'self': url_for(
                '.collections_item',
                pid_value=comid.pid_value,
                collection_id=id,
            )
        }
        return jsonify(json_response), 201


class ItemResource(MethodView):
    """Community inclusion request item endpoint."""

    put_args = {
        # TODO: Check logic for changing a collection ID
        # 'id': fields.String(
        #     location='json',
        #     required=False,
        # ),
        'title': fields.String(
            location='json',
            required=True,
        ),
        'description': fields.String(
            location='json',
            required=False,
        ),
    }

    @pass_community
    @login_required
    @community_permission('get_collection')
    def get(self, comid=None, community=None, collection_id=None, **kwargs):
        """Get the community collection."""
        if collection_id not in community.collections:
            abort(
                404, 'Collection with ID "{}" not found'.format(collection_id))

        collection = community.collections[collection_id]
        json_response = copy.deepcopy(collection)
        json_response['links'] = {
            'self': url_for(
                '.collections_item',
                pid_value=comid.pid_value,
                collection_id=collection_id,
            )
        }
        return jsonify(json_response)

    @use_kwargs(put_args)
    @pass_community
    @login_required
    @community_permission('update_collection')
    def put(self, comid=None, community=None, collection_id=None,
            title=None, description=None, **kwargs):
        """Modify a community collection."""
        if collection_id not in community.collections:
            abort(
                404, 'Collection with ID "{}" not found'.format(collection_id))

        collection = community.collections[collection_id]
        collection.update({
            'title': title,
            'description': description,
        })
        collection.commit()
        db.session.commit()

        json_response = copy.deepcopy(collection)
        json_response['links'] = {
            'self': url_for(
                '.collections_item',
                pid_value=comid.pid_value,
                collection_id=collection_id,
            )
        }
        return jsonify(json_response)

    @pass_community
    @login_required
    @community_permission('delete_collection')
    def delete(self, comid=None, community=None, collection_id=None, **kwargs):
        """Delete the community collection."""
        if collection_id not in community.collections:
            abort(
                404, 'Collection with ID "{}" not found'.format(collection_id))

        # TODO: Explore implications of deleting a collection
        # i.e. ship-off a task to clean-up records that were in it
        del community.collections[collection_id]
        db.session.commit()
        return 'Collection with ID "{}" was deleted'.format(collection_id), 204


class RecordsItemResource(MethodView):
    """Community records list endpoint."""

    put_args = {
        'collections': fields.List(
            fields.Nested({'id': fields.String(required=True)}),
            location='json',
            required=True,
        ),
    }

    @pass_community
    @community_permission('get_record_collections')
    def get(self, comid=None, community=None, record_pid=None, **kwargs):
        """Get a record's collections."""
        recid, record = CommunityRecord.record_cls.resolve(record_pid)
        community_record = community.records[record]
        if community_record is None:
            abort(404,
                'Record with PID "{}" not in community'.format(record_pid))
        return jsonify(community_record.as_dict())

    @use_kwargs(put_args)
    @pass_community
    @login_required
    @community_permission('update_record_collections')
    def put(self, comid=None, community=None, record_pid=None,
            collections=None, **kwargs):
        """Update a record's collections."""
        recid, record = CommunityRecord.record_cls.resolve(record_pid)
        community_record = community.records[record]
        if community_record is None:
            abort(404,
                'Record with PID "{}" not in community'.format(record_pid))

        for c in collections:
            if c['id'] not in community.collections:
                abort(
                    400,
                    'Collection with ID "{id}" not in community'.format(**c)
                )

        community_record['_collections'] = collections
        community_record.commit()
        db.session.commit()

        RecordIndexer().index_by_id(record.id)
        return jsonify(community_record.as_dict())


api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/collections'.format(pid=comid_url_converter),
    view_func=ListResource.as_view('collections_list'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/collections/<collection_id>'.format(pid=comid_url_converter),
    view_func=ItemResource.as_view('collections_item'),
)

api_blueprint.add_url_rule(
    '/communities/<{pid}:pid_value>'
    '/records/<record_pid>'.format(pid=comid_url_converter),
    view_func=RecordsItemResource.as_view('records'),
)
