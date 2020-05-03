# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Records API."""

from __future__ import absolute_import, print_function

from collections import defaultdict
from enum import Enum

from flask import url_for
from invenio_db import db
from invenio_records.api import Record as RecordBaseAPI
from werkzeug.local import LocalProxy

from invenio_communities.api import Community, PIDRecordMixin
from invenio_communities.records.models import \
    CommunityRecord as CommunityRecordModel
from invenio_communities.records.models import CommunityRecordStatus
from invenio_communities.requests.api import RequestBase


# TODO: See if this can be moved to config
class Record(RecordBaseAPI, PIDRecordMixin):
    """PID-aware record."""

    object_type = 'rec'
    pid_type = 'recid'


class CommunityInclusionRequest(RequestBase):

    TYPE = 'community-inclusion-request'

    # TODO: see how to implement or if needed at all...
    community_record_cls = LocalProxy(lambda: CommunityRecord)

    # TODO: Override
    schema = {
        "type": {
            "type": "string",
            # "enum": ["community-inclusion"],
        },
        "state": {
            "type": "string",
            # "enum": ["pending", "closed"],
        },
        "assignees": {"type": "int[]"},
        "created_by": {"type": "int"},
    }

    # TODO: implement "state" property with getter/setter?
    class State(Enum):
        OPEN = 'open'
        CLOSED = 'closed'

    @property
    def community_record(self):
        """Get request's community record relatinship."""
        if not getattr(self, '_community_record', None):
            self._community_record = \
                self.community_record_cls.get_by_request_id(request_id=self.id)
        return self._community_record

    @property
    def community(self):
        """Get request community."""
        return self.community_record.community

    @property
    def record(self):
        """Get request record."""
        return self.community_record.record

    @classmethod
    def create(cls, owner, id_=None, **kwargs):
        """Create a community inclusion request."""
        data = {
            'type': cls.TYPE,
            'state': cls.State.OPEN.value,
            'created_by': owner.id,
            **kwargs,
        }
        model = cls.model_cls(
            owner_id=owner.id,
            json=data,
            id=id_,
        )
        db.session.add(model)
        return cls(data, model=model)

    def as_dict(self):
        return {
            'id': self.id,
            'created': self.created,
            'updated': self.updated,
            'comments': [
                {
                    'id': c.id,
                    'message': c.message,
                    'created_by': c.created_by,
                    'created': c.created,
                    'updated': c.updated,
                } for c in self.comments
            ],
        }

    # TODO: Probably part of view/controller
    @classmethod
    def dump_links(cls, request, pid_value):
        actions = ['comment', 'accept', 'reject']
        links = {
            "self": url_for(
                'invenio_communities_records.requests_item',
                pid_value=pid_value,
                request_id=request.id
            )
        }
        for action in actions:
            links[action] = url_for(
                'invenio_communities_records.requests_item_actions',
                pid_value=pid_value,
                request_id=request.id,
                action=action
            )
        return links


class RecordCommunitiesMixin(PIDRecordMixin):

    record_communities_iter_cls = LocalProxy(
        lambda: RecordCommunitiesCollection)

    object_type = 'rec'
    pid_type = 'recid'

    @property
    def communities(self):
        return self.record_communities_iter_cls(self)

    # TODO: Take into account in the controllers
    # def block_community(cls, community):
    #     # TODO: should this be implemented on the level of Request API
    #     # TODO create a CommunityMember relationship restricting this
    #     pass


class CommunityRecord(RecordBaseAPI):
    """Community-record API class."""

    model_cls = CommunityRecordModel
    community_cls = Community
    record_cls = Record

    schema = {
        # TODO: Define schema
    }

    Status = CommunityRecordStatus

    @property
    def request(self):
        """Community record request."""
        # TODO: Return a RequestRecord object, not the SQLAlchemy model
        if self.model:
            return CommunityInclusionRequest(
                self.model.request.json, self.model.request)
        else:
            return None

    @property
    def status(self):
        """Get community record relationship status."""
        return self.model.status if self.model else None

    @status.setter
    def status(self, new_status):
        """Set community record relationship status."""
        self.model.status = new_status

    @property
    def community(self):
        """Get request's community record relatinship."""
        if not getattr(self, '_community', None):
            self._community = self.community_cls.get_record(
                self.model.community_pid.object_uuid)
        return self._community

    @property
    def record(self):
        """Get request's community record relatinship."""
        if not getattr(self, '_record', None):
            self._record = self.record_cls.get_record(
                self.model.record_pid.object_uuid)
        return self._record

    @classmethod
    def create(cls, record, record_pid, community, request, status=None,
               can_curate=False, data=None):
        data = data or {}
        model = CommunityRecordModel.create(
            community_pid_id=community.pid.id,
            record_pid_id=record_pid.id,
            request_id=request.id,
            status=status,
            json=data,
        )
        obj = cls(data, model=model)
        obj._community = community
        obj._record = record
        return obj

    def delete(self):
        """Delete community record relationship."""
        with db.session.begin_nested():
            db.session.delete(self.model)
        return self

    @classmethod
    def get_by_pids(cls, community_pid, record_pid):
        """Get by community and record PIDs."""
        model = CommunityRecordModel.query.filter_by(
            community_pid_id=community_pid.id,
            record_pid_id=record_pid.id,
        ).one_or_none()
        if not model:
            return None
        return cls(model.json, model=model)

    @classmethod
    def get_by_request_id(cls, request_id):
        """Get by request ID."""
        model = CommunityRecordModel.query.filter_by(
            request_id=request_id
        ).one_or_none()
        if not model:
            return None
        return cls(model.json, model=model)

    def as_dict(self, include_request=True):
        res = {
            'status': str(self.status.title),
            'record_pid': self.record.pid.pid_value,
        }
        if include_request:
            res['request'] = self.request.as_dict()
        else:
            res['request_id'] = self.request.id
        return res

    # TODO: sanity check this
    @property
    def record_pid_value(self):
        return self.model.record_pid.pid_value

    # TODO: sanity check this
    @property
    def community_pid_value(self):
        return self.model.community_pid.pid_value


class CommunityRecordsCollectionBase:

    community_record_cls = CommunityRecord

    def __len__(self):
        """Get number of community records."""
        return self._query.count()

    def __iter__(self):
        self._it = iter(self._query)
        return self

    def filter(self, conditions):
        new_query = self._query.filter_by(**conditions)
        return self.__class__(self.community, _query=new_query)

    def __next__(self):
        """Get next community record item."""
        obj = next(self._it)
        return self.community_record_cls(obj.json, model=obj)

    def __getitem__(self, key):
        raise NotImplementedError()


class CommunityRecordsCollection(CommunityRecordsCollectionBase):

    def __init__(self, community, _query=None):
        self.community = community
        # TODO: Make lazier (e.g. via property)
        self._query = _query or CommunityRecordModel.query.filter_by(
            community_pid_id=self.community.pid.id)

    # TODO: implement if needed
    # def __contains__(self, item):
    #     pass

    def __getitem__(self, record):
        """Get a specific community record by record PID."""
        return self.community_record_cls.get_by_pids(
            self.community.pid, record.pid)

    def add(self, record, request):
        return self.community_record_cls.create(
            self.community, record, request)

    def remove(self, record):
        community_record = self[record]
        return community_record.delete()

    def as_dict(self, include_request=False):
        community_records = defaultdict(list)
        for community_record in self:
            status = community_record.status.name.lower()
            community_records[status].append(community_record.as_dict(
                include_request=include_request))
        return community_records


class RecordCommunitiesCollection(CommunityRecordsCollectionBase):

    def __init__(self, record, _query=None):
        self.record = record
        # TODO: Make lazier (e.g. via property)
        self._query = _query or CommunityRecordModel.query.filter_by(
            record_pid_id=self.record.pid.id)

    def filter(self, conditions):
        new_query = self._query.filter_by(**conditions)
        return self.__class__(self.community, _query=new_query)

    def __getitem__(self, community):
        """Get a specific community record."""
        return self.community_record_cls.get_by_pids(
            community.pid, self.record.pid)

    def add(self, community, request):
        return self.community_record_cls.create(
            community, self.record, request)

    def remove(self, community):
        community_record = self[community]
        return community_record.delete()

    def as_dict(self):
        res = defaultdict(list)
        for community_record in self:
            status = community_record.status.name.lower()
            res[status].append({
                'id': community_record.community.pid.object_uuid,
                'comid': community_record.community.pid.pid_value,
                'title': community_record.community['title'],
                # TODO: Add when implemented
                # 'logo': None,
                'request_id': str(community_record.request.id),
                'created_by': community_record.request['created_by'],
            })
        return res


class CommunityRecordsMixin:

    community_records_iter_cls = CommunityRecordsCollection

    @property
    def records(self):
        return self.community_records_iter_cls(self)

    # TODO: Take into account in the controllers
    # @property
    # def notified_members(self):
    #     pass
    # @property
    # def allowed_record_integrators(self):
    #     pass
    # @property
    # def banned_record_integrators(self):
    #     pass
