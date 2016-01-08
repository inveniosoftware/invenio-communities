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

"""Inject provisional communities."""

from .models import InclusionRequest


def inject_provisional_community(sender, json=None, record=None):
    """Inject 'provisional_communities' key to ES index."""
    q = InclusionRequest.query.filter_by(id_record=record.id)
    provisional_communities_ids = [r.id_community for r in q]
    json['provisional_communities'] = provisional_communities_ids
