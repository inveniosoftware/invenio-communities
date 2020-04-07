# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions for records integration."""

import uuid

from flask.views import MethodView
from flask import Blueprint, render_template, jsonify
from ..views import pass_community, pass_community_function, use_args, use_kwargs
from webargs import fields
from flask_login import current_user


api_blueprint = Blueprint(
    'invenio_communities_records',
    __name__,
    template_folder='../templates',
)


class CommunityRecordsResource(MethodView):
    """Resource for creating and listing community record requests."""

    post_args = {
        'record_pid': fields.String(
            location='json',
            required=True,
        ),
        'message': fields.String(
            location='json',
            required=False,
        )
    }

    @pass_community
    def get(self, pid=None, community=None):
        """List the community record requests."""
        return jsonify({
            "results": [
                {
                    "request_id": str(uuid.uuid4()),
                    "record_pid": 12345,
                    "community_pid": pid.pid_value,
                    "comments": [
                        {"message": "...", "created": "<date>", "created_by": 2},
                    ],
                }
            ]
        })


    @use_kwargs(post_args)
    @pass_community
    def post(self, pid=None, community=None, record_pid=None, message=None,
             **kwargs):
        """Join a community or invite a user to it."""
        return jsonify({
            {
                "request_id": str(uuid.uuid4()),
                "record_pid": record_pid,
                "community_pid": pid.pid_value,
                "comments": [
                    {"message": message, "created": "<date>", "created_by": current_user.id},
                ],
            }
        })

api_blueprint.add_url_rule(
    '/communities/<{0}:pid_value>/requests/inclusion'.format(
        'pid(comid,record_class="invenio_communities.api:Community",'
        'object_type="com")'),
    view_func=CommunityRecordsResource.as_view('requests_list'),
)


ui_blueprint = Blueprint(
    'invenio_communities_records',
    __name__,
    template_folder='../templates',
)


@ui_blueprint.route('/communities/<{0}:pid_value>/curate'.format(
            'pid(comid,record_class="invenio_communities.api:Community",'
            'object_type="com")'))
@pass_community_function
def curation(community, pid):
    """Create a new community."""
    return render_template(
        'invenio_communities/curation.html', community=community, pid=pid)
