# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities."""

from datetime import datetime, timedelta

from elasticsearch_dsl import Q
from flask import session
from invenio_records_resources.services.errors import PermissionDeniedError

from .communities.services.permissions import CommunityNeed

# from datetime import timedelta
# from functools import partial

# from flask import current_app, render_template, request
# from flask_babelex import gettext as _
# from flask_mail import Message
# from invenio_accounts.models import User
# from invenio_base.utils import obj_or_import_string
# from invenio_mail.tasks import send_email
# from invenio_pidstore.resolver import Resolver
# from invenio_records.api import Record
# from invenio_records_rest.utils import LazyPIDValue
# from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
# from werkzeug.routing import BaseConverter
# from werkzeug.utils import cached_property

# # from .members.api import CommunityMember
# # from .members.models import CommunityMemberRole, CommunityMemberStatus


# def format_url_template(url_template, absolute=True, **kwargs):
#     """Formats a URL template-like string."""
#     scheme, netloc, path, query, fragment = urlsplit(url_template)
#     scheme = scheme or request.scheme
#     netloc = netloc or request.host

#     # TODO: Find a more specific exception to raise here (or custom)
#     if absolute:
#         assert netloc
#     path = path.format(**kwargs)
#     query = urlencode({
#         k: [v.format(**kwargs) for v in vals]
#         for k, vals in parse_qs(query).items()
#     }, doseq=True)
#     return urlunsplit((scheme, netloc, path, query, fragment))


# def send_invitation_email(membership, recipients, community, token=b''):
#     """Send email notification for a member invitation or request."""
#     msg = Message(
#         _("Community membership invitation"),
#         sender=current_app.config.get('SUPPORT_EMAIL'),
#         recipients=recipients,
#     )
#     template = ("member_invitation_email.tpl" if membership.request.is_invite
#                 else "member_request_email.tpl")
#     msg.body = render_template(
#         "invenio_communities/email/{}".format(template),
#         community=community,
#         days=timedelta(
#             seconds=current_app.config[
#                 "COMMUNITIES_MEMBERSHIP_REQUESTS_CONFIRMLINK_EXPIRES_IN"]
#         ).days,
#         membership=membership,
#         invitation_link=format_url_template(
#             current_app.config.get(
#                 'COMMUNITIES_INVITATION_LINK_URL',
#                 '/communities/{com_id}/members/requests/{mem_id}?token={token}'
#             ),
#             mem_id=str(membership.id),
#             com_id=community["id"],
#             token=token.decode("utf-8")
#         ),
#         community_members_link=format_url_template(
#             '/communities/{com_id}/members?tab=pending',
#             com_id=community["id"]
#         )
#     )
#     send_email.delay(msg.__dict__)


# def send_inclusion_email(community_record, recipients):
#     """Send email notification for a record invitation or request."""
#     msg = Message(
#         _("Community record inclusion"),
#         sender=current_app.config.get('SUPPORT_EMAIL'),
#         recipients=recipients,
#     )
#     template = ("record_invitation_email.tpl" if
#                 community_record.request.is_invite
#                 else "record_request_email.tpl")
#     msg.body = render_template(
#         "invenio_communities/email/{}".format(template),
#         community_record=community_record,
#         record_invitation_link=format_url_template(
#             current_app.config.get(
#                 'COMMUNITIES_RECORD_INVITATION_LINK_URL',
#                 '/records/{recid}'
#             ),
#             recid=community_record.record.pid.pid_value
#         ),
#         # TODO: make overridable
#         community_curation_link=format_url_template(
#             '/communities/{com_id}/curate?q=',
#             com_id=community_record.community["id"]
#         )
#     )
#     send_email.delay(msg.__dict__)


# # TODO: Remove when
# # https://github.com/inveniosoftware/invenio-records-rest/pull/294 is merged
# class LazyPIDConverter(BaseConverter):
#     """Converter for PID values in the route mapping."""

#     def __init__(self, url_map, pid_type, getter=None, record_class=None,
#                  object_type='rec'):
#         """Initialize the converter."""
#         super(LazyPIDConverter, self).__init__(url_map)
#         self.pid_type = pid_type
#         self.getter = getter
#         self.record_class = record_class
#         self.object_type = object_type

#     @cached_property
#     def resolver(self):
#         """PID resolver."""
#         record_cls = obj_or_import_string(
#             self.record_class, default=Record)
#         getter = obj_or_import_string(
#             self.getter,
#             default=partial(record_cls.get_record, with_deleted=True))
#         return Resolver(
#             pid_type=self.pid_type,
#             object_type=self.object_type,
#             getter=getter
#         )

#     def to_python(self, value):
#         """Resolve PID value."""
#         return LazyPIDValue(self.resolver, value)


# comid_url_converter = (
#     'lazy_pid(comid,'
#     'record_class="invenio_communities:Community",'
#     'object_type="com")'
# )


# # def set_default_admin(community):
# #     """Set the Admin in a newly created community."""
# #     user = User.query.get(community['created_by'])
# #     CommunityMember.create(
# #         community=community,
# #         role=CommunityMemberRole.ADMIN,
# #         user=user,
# #         status=CommunityMemberStatus.ACCEPTED
# #     )


def search_communities(service, identity):
    """Search for communities owned by the given identity.

    We cannot use high-level service functions here because the given
    identity may not be fully initialized yet, and thus fail permission
    checks.
    """
    # TODO this needs to be revisited once memberships are in!
    search_result = service._search(
        'search',
        identity,
        params={},
        es_preference=None,
        extra_filter=Q(
            "term",
            **{"access.owned_by.user": identity.id}
        ),
        permission_action='read',
    ).execute()

    return search_result


def load_community_needs(identity, service):
    """Add community-related needs to the freshly loaded identity.

    Note that this function is intended to be called as handler for the
    identity-loaded signal, where we don't have control over the handler
    execution order.
    Thus, the given identity may not be fully initialized and still missing
    some needs (e.g. 'authenticated_user'), so we cannot rely on high-level
    service functions because permission checks may fail.
    """
    if identity.id is None:
        # no user is logged in
        return

    # NOTE: this function would get called on each page load, so we want to
    #       cache the search results
    COMMUNITY_NEEDS_KEY = "communities-community-needs"
    EXPIRATION_KEY = "communities-needs-cache-expires"
    community_needs = session.get(COMMUNITY_NEEDS_KEY, None)

    # TODO we have to somehow invalidate the cache when the user is added
    #      to more communities!
    now = datetime.utcnow()
    expires_at = session.get(EXPIRATION_KEY, None)
    if expires_at is None or expires_at < now:
        community_needs = None

    try:
        if community_needs is None:
            # if there's nothing cached, start the community search
            community_needs = []
            in_ten_minutes = now + timedelta(minutes=10)
            expires_at = session[EXPIRATION_KEY] = in_ten_minutes

            # NOTE: we cannot use the service method here, because the
            #       identity may not be fully loaded yet, and thus miss
            #       some required needs (e.g. 'authenticated_user')
            for community in search_communities(service, identity):
                community_needs.append(CommunityNeed(str(community.id)))

        # add the needs for all results to the identity
        for need in community_needs:
            identity.provides.add(need)

    except PermissionDeniedError:
        community_needs = []

    finally:
        session[COMMUNITY_NEEDS_KEY] = set(community_needs or [])
