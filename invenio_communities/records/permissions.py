# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community record permissions."""

from flask_principal import UserNeed
from invenio_access.permissions import any_user
from invenio_records_permissions.generators import Generator
from invenio_records_permissions.policies import BasePermissionPolicy

from invenio_communities.permissions import CommunityOwner


class RecordOwners(Generator):
    """Allows record owners."""

    def needs(self, community_record=None, record=None, **kwargs):
        """Enabling Needs."""
        record = record or community_record.record
        return [UserNeed(owner) for owner in record.get('_owners', [])]


class InclusionRequestHandlers(Generator):

    def needs(self, community_record=None, community=None, **kwargs):
        """Skip check at this stage if the membership is an invitation."""
        inclusion_request = community_record.request
        if inclusion_request['state'] == inclusion_request.STATES['CLOSED']:
            return []
        if inclusion_request.is_invite:
            return RecordOwners().needs(record=community_record.record)
        else:
            return CommunityOwner().needs(community=community)



class CommunityRecordPermissionPolicy(BasePermissionPolicy):

    can_list_community_inclusions = [CommunityOwner()]
    can_create_community_inclusion = [RecordOwners(), CommunityOwner()]
    can_get_community_inclusion = [RecordOwners(), CommunityOwner()]
    can_delete_community_inclusion = [RecordOwners(), CommunityOwner()]
    can_handle_community_inclusion = [InclusionRequestHandlers()]
    can_comment_community_inclusion = [RecordOwners(), CommunityOwner()]


def is_permitted_action(action, **kwargs):
    """Helper function to apply a permission check."""
    return CommunityRecordPermissionPolicy(action=action, **kwargs)
