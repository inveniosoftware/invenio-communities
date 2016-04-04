# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Community module receivers."""

import logging

from flask import current_app
from invenio_db import db

from .models import InclusionRequest
from .utils import get_oaiset_spec

logger = logging.getLogger('invenio-communities')


def inject_provisional_community(sender, json=None, record=None, index=None,
                                 **kwargs):
    """Inject 'provisional_communities' key to ES index."""
    if index and not index.startswith(
            current_app.config['COMMUNITIES_INDEX_PREFIX']):
        return

    q = InclusionRequest.query.filter_by(id_record=record.id)
    provisional_communities_ids = [r.id_community for r in q]
    json['provisional_communities'] = provisional_communities_ids


def create_oaipmh_set(mapper, connection, community):
    """Signal for creating OAI-PMH sets during community creation."""
    from invenio_oaiserver.models import OAISet
    with db.session.begin_nested():
        obj = OAISet(spec=get_oaiset_spec(community.id),
                     name=community.title,
                     description=community.description,
                     search_pattern='community:"{0}"'.format(community.id))
        db.session.add(obj)


def destroy_oaipmh_set(mapper, connection, community):
    """Signal for creating OAI-PMH sets during community creation."""
    from invenio_oaiserver.models import OAISet
    with db.session.begin_nested():
        oaiset = OAISet.query.filter_by(
            spec=get_oaiset_spec(community.id)).one_or_none()
        if oaiset is None:
            err = "OAISet for community {0} is missing".format(community.id)
            logger.exception(err)
            raise Exception(err)
        db.session.delete(oaiset)
