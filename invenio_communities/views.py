# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Blueprint definitions for communities core."""

from __future__ import absolute_import, print_function

from functools import partial, wraps

from flask import Blueprint, render_template, request
from flask_login import login_required
from flask_menu import current_menu
from invenio_records_rest.errors import PIDResolveRESTError
from invenio_rest.errors import FieldError, RESTValidationError
from sqlalchemy.exc import SQLAlchemyError
from webargs import ValidationError
from webargs.flaskparser import FlaskParser as FlaskParserBase

from invenio_communities.records.api import CommunityRecordsCollection

from .utils import comid_url_converter


class FlaskParser(FlaskParserBase):
    """Parser to add FieldError to validation errors."""

    def handle_error(self, error, *args, **kwargs):
        """Handle errors during parsing."""
        if isinstance(error, ValidationError):
            _errors = []
            for field, messages in error.messages.items():
                _errors.extend([FieldError(field, msg) for msg in messages])
            raise RESTValidationError(errors=_errors)
        super(FlaskParser, self).handle_error(error, *args, **kwargs)


webargs_parser = FlaskParser()
use_args = webargs_parser.use_args
use_kwargs = webargs_parser.use_kwargs


def pass_community(func=None, view_arg_name='pid_value'):
    """Decorator to retrieve persistent identifier and community."""
    if func is None:
        return partial(pass_community, view_arg_name=view_arg_name)

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            del kwargs[view_arg_name]
            value = request.view_args[view_arg_name]
            comid, community = value.data
        except SQLAlchemyError:
            raise PIDResolveRESTError(value)
        return func(*args, comid=comid, community=community, **kwargs)
    return inner


ui_blueprint = Blueprint(
    'invenio_communities',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@ui_blueprint.before_app_first_request
def init_menu():
    """Initialize menu before first request."""
    item = current_menu.submenu('main.communities')
    item.register(
        'invenio_communities.index',
        'Communities',
        order=3,
    )


@ui_blueprint.route('/communities')
def index():
    """Search communities."""
    return render_template('invenio_communities/index.html')


@ui_blueprint.route('/communities/new')
@login_required
def new():
    """Create a new community."""
    return render_template('invenio_communities/new.html')


@ui_blueprint.route(
    '/communities/<{pid}:pid_value>'.format(pid=comid_url_converter))
@pass_community
def community_page(comid=None, community=None):
    """Members of a community."""
    pending_records = \
        len(CommunityRecordsCollection(community).filter({'status': 'P'}))
    return render_template(
        'invenio_communities/community_page.html',
        community=community,
        comid=comid,
        pending_records=pending_records
    )


@ui_blueprint.route(
    '/communities/<{pid}:pid_value>/settings'.format(pid=comid_url_converter))
@pass_community
@login_required
def settings(comid=None, community=None):
    """Modify a community."""
    pending_records = \
        len(CommunityRecordsCollection(community).filter({'status': 'P'}))
    return render_template(
        'invenio_communities/settings.html',
        community=community,
        comid=comid,
        pending_records=pending_records)
