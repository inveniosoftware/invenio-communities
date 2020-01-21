# -*- coding: utf-8 -*-
#
# This file is part of Zenodo.
# Copyright (C) 2015, 2016 CERN.
#
# Zenodo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Zenodo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Zenodo. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Token serializers."""

from __future__ import absolute_import, print_function

import binascii
import os
from base64 import urlsafe_b64encode
from datetime import datetime

from flask_security import current_user
from flask import current_app
from itsdangerous import BadData, JSONWebSignatureSerializer, \
    SignatureExpired, TimedJSONWebSignatureSerializer
from datetime import timedelta

from flask import current_app, render_template, url_for
from flask_babelex import gettext as _
from flask_mail import Message
from invenio_mail.tasks import send_email


def send_email_invitation(request_id, emails, community, role=None):
    """Receiver for request-created signal to send email notification."""
    for email in emails:
        _send_notification(
            email,
            _("Access request verification"),
            "invenio_communities/emails/request_email.tpl",
            community=community,
            days=timedelta(
                seconds=current_app.config[
                    "COMMUNITIES_MEMBERSHIP_REQUESTS_CONFIRMLINK_EXPIRES_IN"]
            ).days,
            confirm_link=url_for(
                "invenio_communities.community_requests_api",
                membership_request_id=request_id,
                _external=True,
            )
        )
    return token


def _send_notification(to, subject, template, **ctx):
    """Render a template and send as email."""
    msg = Message(
        subject,
        sender=current_app.config.get('SUPPORT_EMAIL'),
        recipients=[to]
    )
    msg.body = render_template(template, **ctx)

    send_email.delay(msg.__dict__)
