# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_db import db
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore.models import PersistentIdentifier
from invenio_pidstore.resolver import Resolver
from invenio_records.api import Record
from werkzeug.local import LocalProxy

from invenio_communities.members.models import CommunityMetadata

from .members.api import CommunityMembersAPI


# TODO: Move somewhere appropriate (`invenio-records-pidstore`)
class PIDRecordMixin:
    """Persistent identifier mixin for records."""

    object_type = None
    pid_type = None

    @property
    def pid(self):
        """Return primary persistent identifier of the record."""
        return PersistentIdentifier.query.filter_by(
            object_uuid=self.id,
            object_type=self.object_type,
            pid_type=self.pid_type
        ).one()

    @classmethod
    def resolve(cls, pid_value):
        """Resolve a PID value and return the PID and record."""
        return Resolver(
            pid_type=cls.pid_type,
            object_type=cls.object_type,
            getter=cls.get_record
        ).resolve(pid_value)

    # TODO: See if needed or if it should be customizable
    # @property
    # def pids(self):
    #     """Return all persistent identifiers of the record."""
    #     return PersistentIdentifier.query.filter_by(
    #         object_uuid=self.id,
    #         object_type=self.object_type,
    #     ).all()


class CommunityBase(Record, PIDRecordMixin):
    """Define API for community creation and manipulation."""

    object_type = 'com'
    pid_type = 'comid'

    # TODO: Communities model doesn't have versioninig, some methods from
    # "invenio_records.api.RecordBase" have to be overridden/removed
    model_cls = CommunityMetadata

    schema = LocalProxy(lambda: current_jsonschemas.path_to_url(
        current_app.config.get(
            'COMMUNITY_SCHEMA', 'communities/communities-v1.0.0.json')))

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create a new community instance and store it in the database."""
        with db.session.begin_nested():
            data['$schema'] = str(cls.schema)
            community = cls(data)
            community.validate(**kwargs)
            community.model = cls.model_cls(id=id_, json=community)
            db.session.add(community.model)
            # TODO: Move this logic to the controller
            CommunityMembersAPI.set_default_admin(community.model)
        return community

    def clear(self):
        """Clear but preserve the schema field."""
        schema = self['$schema']
        super(CommunityBase, self).clear()
        self['$schema'] = schema

    def delete(self, force=False):
        """Delete a community."""
        with db.session.begin_nested():
            if force:
                db.session.delete(self.model)
            else:
                self.model.delete()
        return self


# TODO: Investigate if there's a cleaner/better way
Community = LocalProxy(
    lambda: current_app.extensions['invenio-communities'].community_cls)
