# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Members API."""

from __future__ import absolute_import, print_function

from collections import defaultdict

from flask import current_app, url_for
from invenio_accounts.models import User
from invenio_db import db
# from invenio_communities.utils import send_invitation_email
from invenio_records.api import Record as RecordBaseAPI
from werkzeug.local import LocalProxy

from invenio_communities.members.models import \
    CommunityMember as CommunityMemberModel
from invenio_communities.members.models import CommunityMemberRole, \
    CommunityMemberStatus
from invenio_communities.requests.api import RequestBase

# from invenio_communities.api import Community


Community = LocalProxy(
    lambda: current_app.extensions['invenio-communities'].community_cls)


class CommunityMemberRequest(RequestBase):
    """Request class for Member objects."""

    TYPE = 'community-member-request'

    community_member_cls = LocalProxy(lambda: CommunityMember)

    schema = {
        "type": {"type": "string"},
        "state": {"type": "string"},
        "created_by": {"type": "int"},
    }

    @classmethod
    def create(cls, owner, id_=None, **kwargs):
        """Create a CommunityMemberRequest."""
        data = {
            'type': cls.TYPE,
            'state': 'OPEN',
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

    @property
    def owner(self):
        """Get owner."""
        if not getattr(self, '_owner', None) and self.model.owner_id:
            self._owner = User.query.get(self.model.owner_id)
        return getattr(self, '_owner', None)

    @property
    def community_member(self):
        """Get request's community record relatinship."""
        if not getattr(self, '_community_member', None):
            self._community_member = \
                self.community_member_cls.get_by_request_id(request_id=self.id)
        return self._community_member

    @property
    def community(self):
        """Get request community."""
        return self.community_member.community

    @property
    def user(self):
        """Get request record."""
        return self.community_member.user

    def as_dict(self):
        """Return the metadata of the request as a dictionary."""
        if self.is_invite:
            request_type = 'invitation'
        else:
            request_type = 'request'
        return {
            'id': self.id,
            'created': self.created,
            'updated': self.updated,
            'comments': [
                {
                    'message': c.message,
                    'created_by': c.created_by,
                    'created': c.created,
                } for c in self.comments
            ],
            'request_type': request_type,
            'email': self.community_member.invitation_id
        }

    @property
    def is_invite(self):
        """Returns true or false depending on the request direction."""
        return bool(self.community_member.invitation_id)

    @property
    def is_closed(self):
        """Returns true or false depending on the state of the request."""
        return self['state'] == 'CLOSED'

    def close_request(self):
        """Close the request after it has been succesfully handled."""
        self['state'] = 'CLOSED'


class ModelProxyProperty(object):
    """Class for initializing property like objects."""

    def __init__(self, name):
        """."""
        self.name = name

    def __get__(self, obj, objtype=None):
        """."""
        return getattr(obj.model, self.name)

    def __set__(self, obj, val):
        """."""
        setattr(obj.model, self.name, val)

class CommunityMember(RecordBaseAPI):
    """Community Member class."""

    model_cls = CommunityMemberModel
    community_cls = Community

    @property
    def request(self):
        """Community member request."""
        if self.model and self.model.request:
            return CommunityMemberRequest(
                self.model.request.json, self.model.request)
        else:
            return None

    @property
    def community(self):
        """Get community."""
        if not getattr(self, '_community', None):
            self._community = self.community_cls.get_record(
                self.model.community_pid.object_uuid)
        return self._community

    @property
    def user(self):
        """Get user."""
        if not getattr(self, '_user', None) and self.model.user_id:
            self._user = User.query.get(self.model.user_id)
        return getattr(self, '_user', None)

    role = ModelProxyProperty('role')

    status = ModelProxyProperty('status')

    invitation_id = ModelProxyProperty('invitation_id')

    user_id = ModelProxyProperty('user_id')

    @classmethod
    def create(cls, community, role, user=None, request=None, invitation_id=None, status=None, data=None):
        """Create a community member relationship."""
        assert invitation_id or user
        data = data or {}
        request_id = request.id if request else None
        model = cls.model_cls.create(
            community_pid_id=community.pid.id,
            user_id=user.id if user else None,
            invitation_id=invitation_id,
            request_id=request_id,
            role=role,
            status=status,
            json=data,
        )
        obj = cls(data, model=model)
        obj._community = community
        if user:
            obj._user = user
        return obj

    def delete(self):
        """Delete community member relationship."""
        return self.model.delete(self.model)

    @classmethod
    def get_by_ids(cls, community_pid, user_id):
        """Get by community and user ID."""
        model = CommunityMemberModel.query.filter_by(
            community_pid_id=community_pid.id,
            user_id=user_id,
        ).one_or_none()
        if not model:
            return None
        return cls(model.json, model=model)

    @classmethod
    def get_by_id(cls, membership_id):
        """Get by community and user ID."""
        model = CommunityMemberModel.query.get(membership_id)
        if not model:
            return None
        return cls(model.json, model=model)

    @classmethod
    def get_by_request_id(cls, request_id):
        """Get by request ID."""
        model = CommunityMemberModel.query.filter_by(
            request_id=request_id
        ).one_or_none()
        if not model:
            return None
        return cls(model.json, model=model)

    # TODO: Remove
    def dump_links(self):
        actions = ['comment', 'accept', 'reject']
        links = {
            "self": url_for(
                'invenio_communities_members.community_requests_api',
                pid_value=self.community.pid.pid_value,
                membership_id=str(self.id)
            )
        }
        for action in actions:
            links[action] = url_for(
                'invenio_communities_members.community_requests_handling_api',
                pid_value=self.community.pid.pid_value,
                membership_id=str(self.id),
                action=action
            )
        return links

    def as_dict(self, include_requests=False):
        res = {
            'id': str(self.id),
            'status': str(self.status.name.lower()),
            'role': str(self.role.name.lower()),
            'user_id': self.user.id if self.user else None,
            'username': self.user.profile._displayname if self.user and self.user.profile else None,
            # TODO: Shouldn't be visible publicly. This data should be
            # removed/cleaned in the controller
            'email': self.invitation_id,
            # TODO: Generate these in the view
            #'links': self.dump_links(),
        }
        if self.request:
            if include_requests:
                res['request'] = self.request.as_dict()
            else:
                res['request_id'] = self.request.id
        return res


class CommunityMembersCollection:
    """Iterator for Community Members."""

    community_member_cls = CommunityMember

    def __init__(self, community, _query=None):
        """Initialize the iterator by providing the community."""
        self.community = community
        self._query = _query or CommunityMemberModel.query.filter_by(
            community_pid_id=self.community.pid.id
        ).order_by(
            CommunityMemberModel.created.desc()
        )

    def __len__(self):
        """Get number of community members."""
        return self._query.count()

    def __iter__(self):
        """Iterate over the DB query."""
        self._it = iter(self._query)
        return self

    def filter(self, **conditions):
        """Filter the members with additional conditions."""
        new_query = self._query.filter_by(**conditions)
        return self.__class__(self.community, _query=new_query)

    def __next__(self):
        """Get next community member item."""
        obj = next(self._it)
        return self.community_member_cls(obj.json, model=obj)

    def __contains__(self, user):
        """Method that checks if a user is part of the community members."""
        if isinstance(user, User):
            user_id = user.id
        elif isinstance(user, int):
            user_id = user
        return bool(self._query.filter_by(user_id=user_id).count())

    def __getitem__(self, user_id):
        """Get a specific community member by user ID."""
        return self.community_member_cls.get_by_ids(
            self.community.pid, user_id)

    def add(self, request, status=CommunityMemberStatus.PENDING, user=None,
            role=CommunityMemberRole.MEMBER, invitation_id=None):
        """Add member to the community."""
        return self.community_member_cls.create(
            community=self.community, request=request, role=role, user=user,
            status=status, invitation_id=invitation_id)

    def remove(self, user):
        """Remove a member from the community."""
        community_member = self[user.id]
        return community_member.delete()

    def paginate(self, page=1, size=20):
        pagination = self._query.paginate(page=int(page), per_page=int(size))
        return [self.community_member_cls(i.json, model=i)
                for i in pagination.items]

    def as_dict(self, include_requests=False, result_iterator=None):
        res = []
        result_iterator = result_iterator or self
        for community_member in result_iterator:
            res.append(community_member.as_dict(
                include_requests=include_requests)
            )
        #TODO add aggregations
        res = {"hits": {
            "total": self._query.count(),
            "hits": res
        }}
        return res

    def aggregate(self, key):
        return self._query.group_by(key).count()

    #TODO check this
    def get_user_membership(self, user_id, **kwargs):
        community_members = self.filter(
            user_id=user_id,
            **kwargs)
        membership_obj = community_members._query.one_or_none()
        if not membership_obj:
            return None
        return self.community_member_cls(
            membership_obj.json, model=membership_obj)


class CommunityMembersMixin:

    community_members_iter_cls = CommunityMembersCollection

    @property
    def members(self):
        return self.community_members_iter_cls(self)
