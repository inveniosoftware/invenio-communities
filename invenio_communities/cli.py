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

"""Click command-line interface for communities management."""

from __future__ import absolute_import, print_function

import click
from flask_cli import with_appcontext
from invenio_db import db
from invenio_records.api import Record

from .models import Community, InclusionRequest


#
# Communities management commands
#


@click.group()
def communities():
    """Management commands for Communities."""


@communities.command()
@click.argument('community_id')
@click.argument('record_id')
@click.option('-a', '--accept', 'accept', is_flag=True, default=False)
@with_appcontext
def request(community_id, record_id, accept):
    """Request a record acceptance to a community."""
    c = Community.get(community_id)
    assert c is not None
    record = Record.get_record(record_id)
    if accept:
        c.add_record(record)
        db.session.commit()
    else:
        InclusionRequest.create(community=c, record=record)
        db.session.commit()


@communities.command()
@click.argument('community_id')
@click.argument('record_id')
@with_appcontext
def remove(community_id, record_id):
    """Remove a record from community."""
    c = Community.get(community_id)
    assert c is not None
    c.remove_record(record_id)
    db.session.commit()
