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
from flask import current_app
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_records_resources.services.custom_fields.errors import (
    CustomFieldsException,
)
from invenio_records_resources.services.custom_fields.mappings import Mapping
from invenio_records_resources.services.custom_fields.validate import (
    validate_custom_fields,
)
from invenio_search import current_search_client
from invenio_search.engine import dsl
from invenio_search.engine import search as search_engine
from invenio_search.utils import build_alias_name

from .fixtures.demo import create_fake_community
from .fixtures.tasks import create_demo_community
from .proxies import current_communities


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


@communities.group()
def custom_fields():
    """Communities custom fields commands."""


@custom_fields.command("init")
@click.option(
    "-f",
    "--field-name",
    type=str,
    required=False,
    multiple=True,
    help="A custom field name to create. If not provided, all custom fields will be created.",
)
@with_appcontext
def create_communities_custom_field(field_name):
    """Creates one or all custom fields for communities.

    $ invenio custom-fields communities create [field].
    """
    available_fields = current_app.config.get("COMMUNITIES_CUSTOM_FIELDS")
    if not available_fields:
        click.secho("No custom fields were configured. Exiting...", fg="green")
        exit(0)
    namespaces = set(current_app.config.get("COMMUNITIES_NAMESPACES").keys())
    try:
        validate_custom_fields(
            given_fields=field_name,
            available_fields=available_fields,
            namespaces=namespaces,
        )
    except CustomFieldsException as e:
        click.secho(
            f"Custom fields configuration is not valid. {e.description}", fg="red"
        )
        exit(1)
    click.secho("Creating communities custom fields...", fg="green")
    # multiple=True makes it an iterable
    properties = Mapping.properties_for_fields(field_name, available_fields)

    try:
        communities_index = dsl.Index(
            build_alias_name(current_communities.service.config.record_cls.index._name),
            using=current_search_client,
        )
        communities_index.put_mapping(body={"properties": properties})
        click.secho("Created all communities custom fields!", fg="green")
    except search_engine.RequestError as e:
        click.secho("An error occured while creating custom fields.", fg="red")
        click.secho(e.info["error"]["reason"], fg="red")


@custom_fields.command("exists")
@click.option(
    "-f",
    "--field-name",
    type=str,
    required=True,
    multiple=False,
    help="A custom field name to check.",
)
@with_appcontext
def custom_field_exists_in_communities(field_name):
    """Checks if a custom field exists in communities ES mapping.

    $ invenio custom-fields communities exists <field name>.
    """
    click.secho("Checking custom field...", fg="green")
    communities_index = dsl.Index(
        build_alias_name(current_communities.service.config.record_cls.index._name),
        using=current_search_client,
    )

    field_exists = Mapping.field_exists(
        f"custom_fields.{field_name}", communities_index
    )
    if field_exists:
        click.secho(f"Field {field_name} exists", fg="green")
    else:
        click.secho(f"Field {field_name} does not exist", fg="red")
