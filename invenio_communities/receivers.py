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

from flask import current_app
from invenio_db import db

from .models import InclusionRequest


def inject_provisional_community(sender, json=None, record=None):
    """Inject 'provisional_communities' key to ES index."""
    q = InclusionRequest.query.filter_by(id_record=record.id)
    provisional_communities_ids = [r.id_community for r in q]
    json['provisional_communities'] = provisional_communities_ids


def create_oaipmh_set(mapper, connection, community):
    """Signal for creating OAI-PMH sets during community creation."""
    from invenio_oaiserver.models import OAISet
    with db.session.begin_nested():
        oai_spec = "{0}{1}".format(
                current_app.config["COMMUNITIES_OAI_PREFIX"], community.id)
        obj = OAISet(spec=oai_spec,
                     name=community.title,
                     description=community.description,
                     search_pattern='community:"{0}"'.format(community.id))
        db.session.add(obj)
