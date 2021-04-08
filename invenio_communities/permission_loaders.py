# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Identity changed loaders."""

# from flask_security import current_user

# from invenio_communities.members.models import CommunityMember, \
#     CommunityMemberStatus

# from .members.permissions import CommunityMemberNeed


# TODO: communities-issue
def load_permissions_on_identity_loaded(sender, identity):
    """Add community roles "CommunityMemberNeed" to users' identities."""
    pass
    # if current_user.is_authenticated:
    #     CommunityMember.query.filter_by(
    #         status=CommunityMemberStatus.ACCEPTED,
    #         user_id=int(current_user.get_id()))
    #     for membership in CommunityMember.query.filter_by(
    #             user_id=int(current_user.get_id()),
    #             status=CommunityMemberStatus.ACCEPTED):
    #         if membership.status == CommunityMemberStatus.ACCEPTED:
    #             identity.provides.add(CommunityMemberNeed(
    #                 membership.community_pid.id,
    #                 membership.role.name.lower()
    #             ))
