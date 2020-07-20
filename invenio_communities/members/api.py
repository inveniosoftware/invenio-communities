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
from flask import url_for, current_app

from invenio_communities.requests.models import Request
# from invenio_communities.api import Community

from invenio_communities.members.models import \
    CommunityMember as CommunityMemberModel
from invenio_communities.utils import send_invitation_email
from invenio_records.api import Record as RecordBaseAPI
from invenio_communities.requests.api import RequestBase
from werkzeug.local import LocalProxy
from invenio_accounts.models import User
from invenio_db import db

Community = LocalProxy(
    lambda: current_app.extensions['invenio-communities'].community_cls)
# def create_member_request(comid=None, community=None, email=None, message=None):
#     # TODO: determine "who" is inviting "who"
#     request_user = current_user
#     request = CommunityMemberRequest.create(request_user, id_=uuid.uuid4())
#     try:
#         com_mem = CommunityMember.create(community, invitation_id, request)
#     except:  # check if already exists
#         pass


# # POST /api/comunities/biosyslit/requests/members
# def post(self, comid=None, community=None, email=None,
#         role=None, message=None, **kwargs):
#     request_creator = current_user
#     request_member = User.query.filter_by(email=email).one()
#     request = CommunityMemberRequest.create(
#         request_creator, email, role, id_=uuid.uuid4())
#     send_member_request_email.delay(str(request.id))
#     # serialize response
#     return None


"""

-------- Views layer ------

comm_member = api.CommunityMember.create(community=<api.Community>, user_id=<models.User>)
comm_member.request.accept(...)

-------- API layer --------

    api.Community   <--- api.CommunityMember    ---> models.User
                                  |
                                  v
                        api.CommunityMemberRequest

-------- Models/DB layer --------

models.PID("comid") <--- models.CommunityMember ---> models.User
                                 |
                                 v
                            models.Request


"""

class CommunityMemberRequest(RequestBase):

    TYPE = 'community-member-request'

    # TODO: see how to implement or if needed at all...
    community_member_cls = LocalProxy(lambda: CommunityMember)

    # TODO: Override
    schema = {
        "type": {
            "type": "string",
        },
        "state": {
            "type": "string",
        },
        "created_by": {"type": "int"},
    }

    @classmethod
    def create(cls, owner, id_=None, **kwargs):
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
            'is_invite': self.is_invite,
            'email': self.community_member.invitation_id
        }

    @property
    def is_invite(self):
        """Returns true or false depending on the request direction."""
        return self.community.members.is_admin(self.owner)

    @property
    def is_closed(self):
        """Returns true or false depending on the state of the request."""
        return self['state'] == 'CLOSED'

    def close_request(self):
        """Close the request after it has been succesfully handled."""
        self['state'] = 'CLOSED'


class CommunityMember(RecordBaseAPI):

    model_cls = CommunityMemberModel
    community_cls = Community

    # TODO: figure out what other properties
    @property
    def request(self):
        """Community member request."""
        # TODO check added condition which referes to automatically created relations
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

    # TODO: Find a way to generate this getters/setters smarter
    @property
    def role(self):
        """Get community member relationship role."""
        return self.model.role if self.model else None

    @role.setter
    def role(self, new_role):
        """Set community member relationship role."""
        self.model.role = new_role

    @property
    def status(self):
        """Get community member relationship status."""
        return self.model.status if self.model else None

    @status.setter
    def status(self, new_status):
        """Set community member relationship status."""
        self.model.status = new_status

    @property
    def invitation_id(self):
        """Get community member relationship invitation_id."""
        return self.model.invitation_id if self.model else None

    @invitation_id.setter
    def invitation_id(self, new_invitation_id):
        """Set community member relationship invitation_id."""
        self.model.invitation_id = new_invitation_id

    @property
    def user_id(self):
        """Get community member relationship user_id."""
        return self.model.user_id if self.model else None

    @user_id.setter
    def user_id(self, new_user_id):
        """Set community member relationship user_id."""
        self.model.user_id = new_user_id

    # TODO: do we really need this JSON?
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

    def dump_links(self):
        actions = ['comment', 'accept', 'reject']
        links = {
            "self": url_for(
                'invenio_communities_members.community_requests_management_api',
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
            # TODO: Shouldn't be visible publicly
            'invitation_id': self.invitation_id,
            # TODO: Generate these in the serializer
            'links': self.dump_links(),
        }
        if self.request:
            if include_requests:
                res['request'] = self.request.as_dict()
            else:
                res['request_id'] = self.request.id
        return res


class CommunityMembersCollection:

    community_member_cls = CommunityMember

    def __init__(self, community, _query=None):
        self.community = community
        # TODO: Make lazier (e.g. via property)
        self._query = _query or CommunityMemberModel.query.filter_by(
            community_pid_id=self.community.pid.id
        ).order_by(
            CommunityMemberModel.created.desc()
        )

    def __len__(self):
        """Get number of community members."""
        return self._query.count()

    def __iter__(self):
        self._it = iter(self._query)
        return self

    def filter(self, **conditions):
        new_query = self._query.filter_by(**conditions)
        return self.__class__(self.community, _query=new_query)

    def __next__(self):
        """Get next community member item."""
        obj = next(self._it)
        return self.community_member_cls(obj.json, model=obj)

    def __contains__(self, user):
        return bool(self._query.filter_by(user=user).count())

    def __getitem__(self, user_id):
        """Get a specific community member by user ID."""
        return self.community_member_cls.get_by_ids(
            self.community.pid, user_id)

    def add(self, request, status='P', user=None, role='M', invitation_id=None):
        return self.community_member_cls.create(
            community=self.community, request=request, role=role, user=user,
            status=status, invitation_id=invitation_id)

    def remove(self, user):
        community_member = self[user.id]
        return community_member.delete()

    def paginate(self, page=1, size=20):
        # TODO sorting default by created date
        pagination = self._query.paginate(page=page, per_page=size)
        return [self.community_member_cls(i.json, model=i)
                for i in pagination.items]

    def as_dict(self, include_requests=False):
        res = defaultdict(list)
        for community_member in self:
            status = community_member.status.name.lower()
            #TODO maybe change to include less information
            res[status].append(community_member.as_dict(
                include_requests=include_requests)
                # 'user_id': community_member._user.id,
                # 'email': community_member._user.email,
                # # TODO: Is that needed?
                # 'request_id': str(community_member.request.id),
                # 'created_by': community_member.request['created_by'],
            )
        res = {"hits": {
            "total": len(self._query),
            "hits": res
        }}
        return res

    def aggregate(self, key):
        return self._query.group_by(key).count()

    def is_member(self, user):
        community_members = self.filter(status='A')
        return user.id in [member.model.user_id for member in community_members]

    def is_curator(self, user):
        community_curators = self.filter(role='C', status='A')
        return user.id in [curator.model.user_id for curator in community_curators]

class CommunityMembersMixin:

    community_members_iter_cls = CommunityMembersCollection

    @property
    def members(self):
        return self.community_members_iter_cls(self)
