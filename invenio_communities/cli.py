# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


import random
import uuid

import click
from faker import Faker
from flask import current_app
from flask.cli import with_appcontext
from flask_security.utils import hash_password
from invenio_accounts.models import User
from invenio_db import db
from invenio_pidstore import current_pidstore
from invenio_search import current_search
from sqlalchemy.sql.expression import func
from werkzeug.local import LocalProxy

from invenio_communities.api import Community
from invenio_communities.indexer import CommunityIndexer
from invenio_communities.marshmallow import CommunitySchemaMetadataV1
from invenio_communities.models import CommunityMembers, CommunityMetadata, \
    MembershipRequests

_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)

def create_fake_community():
    """ Create communities for demo purposes."""
    fake = Faker()
    type_accepted = ['organization', 'event', 'topic', 'project']
    visibility_accepted = ['public', 'private', 'hidden']
    data_to_use = {
        "id": fake.word(),
        "title": "fake.text(max_nb_chars=10)",
        "description": fake.text(),
        "page": fake.text(),
        "type": fake.word(ext_word_list=type_accepted),
        "visibility": fake.word(ext_word_list=visibility_accepted)
    }

    data_to_use = CommunitySchemaMetadataV1().load(data_to_use).data

    comm_uuid = uuid.uuid4()
    current_pidstore.minters['comid'](comm_uuid, data_to_use)
    community = Community.create(data_to_use, id_=comm_uuid)
    CommunityIndexer().index(community)

    current_search.flush_and_refresh(index='communities')
    db.session.commit()


@click.group()
def rdm_communities():
    """InvenioRDM communities commands."""
    pass


@rdm_communities.command('demo')
@with_appcontext
def demo_communities():
    """Create 10 fake communities for demo purposes."""
    click.secho('Creating demo communities...', fg='blue')

    for _ in range(10):
        create_fake_community()

    click.secho('Created communities!', fg='green')


def create_fake_member():
    """ Create members for demo purposes."""
    role_accepted = ['A', 'C', 'M']
    fake = Faker()
    data_to_use = {
        "email": fake.email(),
        "password": fake.word(),
        "active": True
    }
    data_to_use['password'] = hash_password(data_to_use['password'])
    _datastore.create_user(**data_to_use)
    data_to_use['password'] = '****'
    db.session.commit()

    last_user = User.query.order_by(User.id.desc()).first()
    community = CommunityMetadata.query.order_by(func.random()).first()
    MembershipRequests.create(
        community.id,
        random.choice([True, False]),
        role=fake.word(ext_word_list=role_accepted),
        user_id=last_user.id)
    db.session.commit()
    CommunityMembers.create(
        MembershipRequests.query.filter_by(
            user_id=last_user.id,
            comm_id=community.id
    ).one())
    db.session.commit()


@click.group()
def rdm_members():
    """InvenioRDM members commands."""
    pass


@rdm_members.command('demo')
@with_appcontext
def demo_members():
    """Create 10 fake members for demo purposes."""
    click.secho('Creating demo members...', fg='blue')

    for _ in range(10):
        create_fake_member()

    click.secho('Created members!', fg='green')
