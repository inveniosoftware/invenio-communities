# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Utilities."""

from __future__ import absolute_import, print_function

from datetime import timedelta
from functools import partial

from flask import current_app, render_template, request
from flask_babelex import gettext as _
from flask_mail import Message
from invenio_mail.tasks import send_email
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record
from invenio_records_rest.utils import LazyPIDValue, obj_or_import_string
from six.moves.urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from werkzeug.routing import BaseConverter
from werkzeug.utils import cached_property


def format_url_template(url_template, absolute=True, **kwargs):
    """Formats a URL template-like string."""
    scheme, netloc, path, query, fragment = urlsplit(url_template)
    scheme = scheme or request.scheme
    netloc = netloc or request.host

    # TODO: Find a more specific exception to raise here (or custom)
    if absolute:
        assert netloc

    path = path.format(**kwargs)
    query = urlencode(
        {k: v.format(**kwargs) for k, v in parse_qs(query).items()})
    return urlunsplit((scheme, netloc, path, query, fragment))


def send_invitation_email(membership_request, recipients, community):
    """Send email notification for a member invitation."""
    msg = Message(
        _("Community membership invitation"),
        sender=current_app.config.get('SUPPORT_EMAIL'),
        recipients=recipients,
    )
    template = ("invitation_email.tpl" if membership_request.is_invite
                else "member_request_email.tpl")
    msg.body = render_template(
        "invenio_communities/{}".format(template),
        community=community,
        days=timedelta(
            seconds=current_app.config[
                "COMMUNITIES_MEMBERSHIP_REQUESTS_CONFIRMLINK_EXPIRES_IN"]
        ).days,
        membership_request=membership_request,
        invitation_link=format_url_template(
            # TODO: change to use value from config
            '/communities/members/requests/{req_id}',
            req_id=str(membership_request.id),
        )
    )
    send_email.delay(msg.__dict__)


# TODO: Remove when
# https://github.com/inveniosoftware/invenio-records-rest/pull/294 is merged
class LazyPIDConverter(BaseConverter):
    """Converter for PID values in the route mapping."""

    def __init__(self, url_map, pid_type, getter=None, record_class=None,
                 object_type='rec'):
        """Initialize the converter."""
        super(LazyPIDConverter, self).__init__(url_map)
        self.pid_type = pid_type
        self.getter = getter
        self.record_class = record_class
        self.object_type = object_type

    @cached_property
    def resolver(self):
        """PID resolver."""
        record_cls = obj_or_import_string(
            self.record_class, default=Record)
        getter = obj_or_import_string(
            self.getter,
            default=partial(record_cls.get_record, with_deleted=True))
        return Resolver(
            pid_type=self.pid_type,
            object_type=self.object_type,
            getter=getter
        )

    def to_python(self, value):
        """Resolve PID value."""
        return LazyPIDValue(self.resolver, value)


comid_url_converter = (
    'lazy_pid(comid,'
    'record_class="invenio_communities.api:Community",'
    'object_type="com")'
)
