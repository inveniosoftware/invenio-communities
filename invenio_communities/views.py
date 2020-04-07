# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Blueprint definitions for communities core."""

from __future__ import absolute_import, print_function

from flask_menu import current_menu
from flask.views import MethodView
from webargs import ValidationError, fields, validate
from webargs.flaskparser import FlaskParser as FlaskParserBase
from invenio_db import db

from functools import wraps
from flask import Blueprint, abort, request, render_template, jsonify
from flask_security import current_user
from sqlalchemy.exc import SQLAlchemyError
from invenio_records_rest.errors import PIDResolveRESTError


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


def pass_community(f):
    """Decorator to retrieve persistent identifier and community.

    This decorator will resolve the ``pid_value`` parameter from the route
    pattern and resolve it to a PID and a community, which are then available
    in the decorated function as ``pid`` and ``community`` kwargs respectively.
    """
    @wraps(f)
    def inner(self, pid_value, *args, **kwargs):
        try:
            pid, community = request.view_args['pid_value'].data
            return f(self, pid=pid, community=community, *args, **kwargs)
        except SQLAlchemyError:
            raise PIDResolveRESTError(pid)

    return inner


def pass_community_function(f):
    """Decorator to retrieve persistent identifier and community.

    This decorator will resolve the ``pid_value`` parameter from the route
    pattern and resolve it to a PID and a community, which are then available
    in the decorated function as ``pid`` and ``community`` kwargs respectively.
    """
    @wraps(f)
    def inner(pid_value, *args, **kwargs):
        try:
            pid, community = request.view_args['pid_value'].data
            return f(pid=pid, community=community, *args, **kwargs)
        except SQLAlchemyError:
            raise PIDResolveRESTError(pid)

    return inner


ui_blueprint = Blueprint(
    'invenio_communities',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@ui_blueprint.route('/communities/<{0}:pid_value>'.format(
            'pid(comid,record_class="invenio_communities.api:Community",'
            'object_type="com")'))
@pass_community_function
def community_page(community, pid):
    """Members of a community."""
    return render_template(
        'invenio_communities/community_page.html',
        community=community,
        pid=pid
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


@ui_blueprint.route('/communities/new')
def new():
    """Create a new community."""
    return render_template('invenio_communities/new.html')


@ui_blueprint.route('/communities/')
def index():
    """Search for a new community."""
    return render_template('invenio_communities/index.html')


@ui_blueprint.route('/communities/<{0}:pid_value>/settings'.format(
            'pid(comid,record_class="invenio_communities.api:Community",'
            'object_type="com")'))
@pass_community_function
def settings(community, pid):
    """Modify a community."""
    return render_template(
        'invenio_communities/settings.html', community=community, pid=pid)
