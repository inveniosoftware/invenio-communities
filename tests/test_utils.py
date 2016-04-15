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


"""Utility functions tests."""

from __future__ import absolute_import, print_function

from invenio_accounts.testutils import create_test_user
from invenio_db import db
from invenio_records.api import Record

from invenio_communities.models import Community, InclusionRequest
from invenio_communities.utils import render_template_to_string


def test_template_formatting_from_string(app):
    """Test formatting of string-based template to string."""
    with app.app_context():
        out = render_template_to_string("foobar: {{ baz }}", _from_string=True,
                                        **{'baz': 'spam'})
        assert out == 'foobar: spam'


def test_email_formatting(app):
    """Test formatting of the email message with the default template."""
    with app.app_context():
        with app.extensions['mail'].record_messages() as outbox:
            # User
            user1 = create_test_user()
            user1.username = 'testuser'
            db.session.add(user1)

            # Community
            comm1 = Community(
                id='comm1', id_user=user1.id, title='FooCommunity')
            rec1 = Record.create({
                'title': 'Foobar and Bazbar',
                'description': 'On Foobar, Bazbar and <b>more</b>.'
            })
            db.session.add(comm1)
            db.session.commit()

            # Request
            InclusionRequest.create(community=comm1, record=rec1, user=user1)

            # Check emails being sent
            assert len(outbox) == 1
            sent_msg = outbox[0]
            assert sent_msg.recipients == [user1.email]
            assert comm1.title in sent_msg.body
