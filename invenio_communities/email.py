# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Token serializers."""

from __future__ import absolute_import, print_function


from datetime import timedelta
from flask import current_app, render_template, url_for
from flask_babelex import gettext as _
from flask_mail import Message

from invenio_mail.tasks import send_email


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
        # TODO: URL needs to change to UI one, but its problematic due to context
        membership_request=membership_request,
        invitation_link=url_for(
            "invenio_communities.community_requests_api",
            membership_request_id=membership_request.id,
            _external=True,
        )
    )
    send_email.delay(msg.__dict__)
