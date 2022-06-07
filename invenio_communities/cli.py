# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command-line tools for demo module."""

import click
from faker import Faker
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity

from invenio_communities.proxies import current_communities

from .fixtures.demo import create_fake_community
from .fixtures.tasks import create_demo_community


@click.group()
def communities():
    """Invenio communities commands."""


@communities.command("demo")
@with_appcontext
def demo():
    """Create 100 fake communities for demo purposes."""
    click.secho("Creating demo communities...", fg="green")
    faker = Faker()
    for _ in range(100):
        fake_data = create_fake_community(faker)
        create_demo_community.delay(fake_data)

    click.secho("Created communities!", fg="green")


@communities.command("rebuild-index")
@with_appcontext
def rebuild_index():
    """Rebuild index."""
    click.secho("Reindexing communities...", fg="green")

    communities_service = current_communities.service
    communities_service.rebuild_index(identity=system_identity)

    click.secho("Reindexed communities!", fg="green")
