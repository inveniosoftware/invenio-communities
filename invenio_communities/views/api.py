# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module that adds API to communities."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort
from invenio_rest import ContentNegotiatedMethodView

from invenio_communities.models import Community
from invenio_communities.serializers.schemas.community import CommunitySchemaV1
from webargs import fields
from webargs.flaskparser import parser, use_kwargs

from invenio_communities.serializers import community_response

blueprint = Blueprint(
    'invenio_communities_api',
    __name__,
    url_prefix='/communities',
)


class CommunitiesResource(ContentNegotiatedMethodView):
    """"Communities resource."""

    get_args = dict(
        query=fields.String(
            location='query',
            load_from='q',
            missing=None,
        ),
        sort=fields.String(
            location='query',
            missing=None,
        ),
        page=fields.Int(
            location='query',
            missing=1,
        ),
        size=fields.Int(
            location='query',
            missing=10,
        )
    )

    def __init__(self, serializers=None, *args, **kwargs):
        """Constructor."""
        super(CommunitiesResource, self).__init__(
            serializers,
            *args,
            **kwargs
        )

    @use_kwargs(get_args)
    def get(self, query, sort, page, size):
        """Get a list of all the communities.

        .. http:get:: /communities/(string:id)
            Returns a JSON list with all the communities.
            **Request**:
            .. sourcecode:: http
                GET /communities HTTP/1.1
                Accept: application/json
                Content-Type: application/json
                Host: localhost:5000
            :reqheader Content-Type: application/json
            **Response**:
            .. sourcecode:: http
                HTTP/1.0 200 OK
                Content-Length: 334
                Content-Type: application/json
                [
                    {
                        "id": "comm1"
                    },
                    {
                        "id": "comm2"
                    }
                ]
            :resheader Content-Type: application/json
            :statuscode 200: no error
        """
        communities = Community.filter_communities(query, sort)
        result = communities.paginate(page, size).items
        return self.make_response(result)


class CommunityDetailsResource(ContentNegotiatedMethodView):
    """"Community details resource."""

    def __init__(self, serializers=None, *args, **kwargs):
        """Constructor."""
        super(CommunityDetailsResource, self).__init__(
            serializers,
            *args,
            **kwargs
        )

    def get(self, community_id):
        """Get the details of the specified community.

        .. http:get:: /communities/(string:id)
            Returns a JSON dictionary with the details of the specified
            community.
            **Request**:
            .. sourcecode:: http
                GET /communities/communities/comm1 HTTP/1.1
                Accept: application/json
                Content-Type: application/json
                Host: localhost:5000
            :reqheader Content-Type: application/json
            :query string id: ID of an specific community to get more
                              information.
            **Response**:
            .. sourcecode:: http
                HTTP/1.0 200 OK
                Content-Length: 334
                Content-Type: application/json
                {
                    "id_user": 1,
                    "description": "",
                    "title": "",
                    "created": "2016-04-05T14:56:37.051462",
                    "id": "comm1",
                    "page": "",
                    "curation_policy": ""
                }

            :resheader Content-Type: application/json
            :statuscode 200: no error
            :statuscode 404: page not found
        """
        community = Community.get(community_id)
        if not community:
            abort(404)
        return self.make_response(community)

serializers = {'application/json': community_response}

communities_view = CommunitiesResource.as_view(
    'communities_api',
    serializers=serializers,
    default_media_type='application/json',
)

community_details_view = CommunityDetailsResource.as_view(
    'commuity_details_api',
    serializers=serializers,
    default_media_type='application/json',
)

blueprint.add_url_rule(
    '/',
    view_func=communities_view,
    methods=['GET']
)

blueprint.add_url_rule(
    '/<string:community_id>',
    view_func=community_details_view,
    methods=['GET']
)
