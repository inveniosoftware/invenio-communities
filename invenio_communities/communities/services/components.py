# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2022 CERN.
# Copyright (C) 2022 Northwestern University.
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

import re

from flask_babelex import lazy_gettext as _

from invenio_access.permissions import system_identity, system_process
from invenio_db import db
from invenio_oaiserver.models import OAISet
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_records_resources.services.records.components import \
    ServiceComponent
from marshmallow.exceptions import ValidationError

from ...proxies import current_communities, current_roles
from ...utils import on_membership_change


class PIDComponent(ServiceComponent):
    """Service component for Community PIDs."""

    @classmethod
    def _validate(cls, pid_value):
        """Checks the validity of the provided pid value."""
        blop = re.compile('^[-\w]+$')
        if not bool(blop.match(pid_value)):
            raise ValidationError(
                'The ID should contain only letters with numbers or dashes.',
                field_name='id',
            )

    def create(self, identity, record=None, data=None, **kwargs):
        """Create a Community PID from its metadata."""
        data['id'] = data['id'].lower()
        self._validate(data['id'])
        record['id'] = data['id']
        try:
            provider = record.__class__.pid.field._provider.create(record=record)
        except PIDAlreadyExists:
            raise ValidationError(
                'A community with this identifier already exists.',
                field_name='id',
            )
        setattr(record, 'pid', provider.pid)

    def update(self, identity, record=None, data=None, **kwargs):
        """Rename the Community PIDs value."""
        if 'id' in data and record.pid.pid_value != data['id']:
            raise ValidationError(
                'The ID should be modified through the renaming URL instead',
                field_name='id',
            )

    def rename(self, identity, record=None, data=None, **kwargs):
        """Rename the Community PIDs value."""
        data['id'] = data['id'].lower()
        if record.pid.pid_value == data['id']:
            raise ValidationError(
                'A new ID value is required for the renaming',
                field_name='id',
            )
        self._validate(data['id'])
        try:
            record.__class__.pid.field._provider.update(
                record.pid, data['id'])
        except PIDAlreadyExists:
            raise ValidationError(
                'A community with this identifier already exists.',
                field_name='id',
            )

# TODO: Move to Invenio-Records-Resources (and make reusable). Duplicated from
# Invenio-RDM-Records.
class AccessComponent(ServiceComponent):
    """Service component for access integration."""

    def _populate_access_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the record's access field."""
        if record is not None and "access" in data:
            # populate the record's access field with the data already
            # validated by marshmallow
            record.update({"access": data.get("access")})
            record.access.refresh_from_dict(record.get("access"))

        errors = record.access.errors
        if errors:
            # filter out duplicate error messages
            messages = list({str(e) for e in errors})
            raise ValidationError(messages, field_name="access")

    def _init_owners(self, identity, record, **kwargs):
        """If the record has no owners yet, add the current user."""
        # if the given identity is that of a user, we add the
        # corresponding user to the owners
        # (record.parent.access.owners) and commit the parent
        # otherwise, the parent's owners stays empty
        is_sys_id = system_process in identity.provides
        if not record.parent.access.owners and not is_sys_id:
            owner_dict = {"user": identity.id}
            record.parent.access.owners.add(owner_dict)
            record.parent.commit()

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        self._populate_access_and_validate(identity, data, record, **kwargs)
        self._init_owners(identity, record, **kwargs)

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_access_and_validate(identity, data, record, **kwargs)

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        record.access = draft.access

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.access = record.access

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft metadata."""
        draft.access = record.access


# TODO: Move to Invenio-Records-Resources (and make reusable). Duplicated from
# Invenio-RDM-Records.
class CommunityAccessComponent(AccessComponent):
    """Service component for access integration."""

    def _populate_access_and_validate(self, identity, data, record, **kwargs):
        """Populate and validate the community's access field."""
        if record is not None and "access" in data:
            # populate the record's access field with the data already
            # validated by marshmallow
            record.setdefault('access', {})
            record['access'].update(data.get("access", {}))
            record.access.refresh_from_dict(record.get("access"))

    def create(self, identity, data=None, record=None, **kwargs):
        """Add basic ownership fields to the record."""
        self._populate_access_and_validate(identity, data, record, **kwargs)

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        self._populate_access_and_validate(identity, data, record, **kwargs)


class OwnershipComponent(ServiceComponent):
    """Service component for owner membership integration."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Make an owner member from the identity."""
        if system_process in identity.provides:
            return

        member = {
            "type": "user",
            "id": str(identity.id),
        }
        self.service.members.add(
            system_identity,
            record.id,
            {"members": [member], "role": current_roles.owner_role.name},
            uow=self.uow,
        )

        # Invalidate the membership cache
        on_membership_change(identity=identity)


class FeaturedCommunityComponent(ServiceComponent):
    """Service component for featured community integration."""
    
    def featured_create(self, identity, data=None, record=None, **kwargs):
        if(record.access.visibility != "public"):
            raise ValidationError(
                _("The community is not public"),
                field_name="community_id"
            )


class OAISetComponent(ServiceComponent):
    """Service component for OAI set integration."""

    _oai_sets_prefix = "community"

    def _retrieve_set(self, id):
        return OAISet.query.filter(OAISet.spec == self._create_set_spec(id)).first()

    def _create_set_spec(self, community_id):
        return "{prefix}-{id}".format(prefix=self._oai_sets_prefix, id=community_id)

    def _create_set_description(self, community_title):
        # NOTE: Does not require translation since this description can also be changed by an admin
        return "Records belonging to the community '{title}'".format(title=community_title)

    def _create_set_from_community(self, record,):
        community_id = record.pid.pid_value
        community_title = record.metadata["title"]

        community_set = OAISet()
        community_set.name = community_title
        community_set.description = self._create_set_description(community_title)
        community_set.spec = self._create_set_spec(community_id)
        community_set.search_pattern = "parent.communities.ids:{id}".format(id=community_id)

        return community_set

    def create(self, identity, data=None, record=None, **kwargs):
        """Create a set for the community."""
        if record.access.visibility != "public":
            return

        community_set = self._create_set_from_community(record)
        # NOTE: will be indexed via a listener in oaiserver module
        db.session.add(community_set)


    def delete(self, identity, data=None, record=None, **kwargs):
        """Remove the set for the community."""
        community_set = self._retrieve_set(kwargs.get("id") or record.pid.pid_value)
        if not community_set:
            return

        # NOTE: will be removed from index via listener in oaiserver module
        db.session.delete(community_set)


    def update(self, identity, data=None, record=None, **kwargs):
        """Update set accordingly."""
        if record.access.visibility != "public":
            # delete set if the community is not public anymore
            self.delete(identity, data, record, **kwargs)
            return

        community_set = self._retrieve_set(record.pid.pid_value)
        if not community_set:
            # create new set because community is now public
            self.create(identity, data, record, **kwargs)
            return

        # just update set with new name and description
        community_set.name = record.metadata["title"]
        community_set.description = self._create_set_description(community_set.name)
        db.session.add(community_set)


    def rename(self, identity, record=None, data=None, **kwargs):
        """Delete old set and create new set on ID change"""
        if record.access.visibility != "public":
            return

        # Since we want to delete the set created with the old set, we can not
        # use the already updated pid_value
        self.delete(identity, data=data, record=record, **kwargs, id=record.get("id"))
        community_set = self._create_set_from_community(record)
        db.session.add(community_set)
