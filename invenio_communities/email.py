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

# TODO: Remove dependency on current_app


class TokenMixin(object):
    """Mix-in class for token serializers."""

    def create_token(self, obj_id):
        """Create a token referencing the object id with extra data.

        Note random data is added to ensure that no two tokens are identical.
        """
        return self.dumps(
            dict(
                id=obj_id,
                rnd=binascii.hexlify(os.urandom(4)).decode('utf-8')
            )
        )

    def validate_token(self, token, expected_data=None):
        """Validate secret link token.

        :param token: Token value.
        :param expected_data: A dictionary of key/values that must be present
            in the data part of the token (i.e. included via ``extra_data`` in
            ``create_token``).
        """
        try:
            # Load token and remove random data.
            data = self.load_token(token)

            # Compare expected data with data in token.
            if expected_data:
                for k in expected_data:
                    if expected_data[k] != data["data"].get(k):
                        return None
            return data
        except BadData:
            return None

    def load_token(self, token, force=False):
        """Load data in a token.

        :param token: Token to load.
        :param force: Load token data even if signature expired.
                      Default: False.
        """
        try:
            data = self.loads(token)
        except SignatureExpired as e:
            if not force:
                raise
            data = e.payload

        del data["rnd"]
        return data


class EmailConfirmationSerializer(TimedJSONWebSignatureSerializer, TokenMixin):
    """Serializer for email confirmation link tokens.

    Depends upon the secrecy of ``SECRET_KEY``. Tokens expire after a specific
    time (defaults to ``ACCESSREQUESTS_CONFIRMLINK_EXPIRES_IN``). The
    access request id as well as the email address is stored in the token
    together with a random bit to ensure all tokens are unique.
    """

    def __init__(self, expires_in=None):
        """Initialize underlying TimedJSONWebSignatureSerializer."""
        dt = expires_in or \
            current_app.config['COMMUNITIES_MEMBERSHIP_REQUESTS_CONFIRMLINK_EXPIRES_IN']

        super(EmailConfirmationSerializer, self).__init__(
            current_app.config['SECRET_KEY'],
            expires_in=dt,
            salt='accessrequests-email',
        )


def send_email_invitation(request_id, emails, community, role=None):
    """Receiver for request-created signal to send email notification."""
    token = EmailConfirmationSerializer().create_token(str(request_id))
    import wdb; wdb.set_trace()
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
                token=token,
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
