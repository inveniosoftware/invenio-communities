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

"""Module tests."""

from __future__ import absolute_import, print_function

from invenio_accounts.testutils import create_test_user
from invenio_db import db
from invenio_records.api import Record

from invenio_communities.models import Community, InclusionRequest


def test_community_delete_task(app):
    """Test the community deletion task."""
    with app.app_context():
        # Init the User and the Community
        user1 = create_test_user()
        comm1 = Community(id='comm1', id_user=user1.id)
        db.session.add(comm1)
        communities_key = app.config["COMMUNITIES_RECORD_KEY"]
        rec1 = Record.create({'title': 'Foobar'})
        InclusionRequest.create(community=comm1, record=rec1, notify=False)
        db.session.commit()
        assert InclusionRequest.get(comm1.id, rec1.id)

        comm1.accept_record(rec1)
        assert 'comm1' in rec1[communities_key]
        db.session.commit()

        comm1.delete()
        assert comm1.is_deleted
