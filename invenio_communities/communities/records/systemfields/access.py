# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community access system field."""

from invenio_records.systemfields import SystemField
from .owners import Owners


class CommunityAccess:
    """Access management per community."""

    VISIBILITY_LEVELS = ('public', 'restricted')
    MEMBER_POLICY_LEVELS = ('open', 'closed')
    RECORD_POLICY_LEVELS = ('open', 'closed', 'restricted')

    owners_cls = Owners

    def __init__(
        self,
        visibility=None,
        member_policy=None,
        record_policy=None,
        owned_by=None,
        owners_cls=None,
    ):
        """Create a new CommunityAccess object.

        If ``owned_by`` is not specified, a new instance of ``owners_cls``
        will be used.

        :param visibility: The visibility level.
        :param owned_by: The set of community owners
        """
        self.visibility = visibility or 'public'
        self.member_policy = member_policy or 'open'
        self.record_policy = record_policy or 'open'

        owners_cls = owners_cls or self.owners_cls
        self.owned_by = owned_by if owned_by else owners_cls()

        self.errors = []

    def _validate_visibility_level(self, level):
        return level in self.VISIBILITY_LEVELS

    def _validate_member_policy_level(self, level):
        return level in self.MEMBER_POLICY_LEVELS

    def _validate_record_policy_level(self, level):
        return level in self.RECORD_POLICY_LEVELS

    @property
    def visibility(self):
        """Get the visibility level."""
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        """Set the visibility level."""
        if not self._validate_visibility_level(value):
            raise ValueError(f"Unknown visibility level: {value}")
        self._visibility = value

    @property
    def member_policy(self):
        """Get the member policy level."""
        return self._member_policy

    @member_policy.setter
    def member_policy(self, value):
        """Set the member policy level."""
        if not self._validate_member_policy_level(value):
            raise ValueError(f"Unknown member policy level: {value}")
        self._member_policy = value

    @property
    def record_policy(self):
        """Get the record policy level."""
        return self._record_policy

    @record_policy.setter
    def record_policy(self, value):
        """Set the record policy level."""
        if not self._validate_record_policy_level(value):
            raise ValueError(f"Unknown record policy level: {value}")
        self._record_policy = value

    def dump(self):
        """Dump the field values as dictionary."""
        return {
            "visibility": self.visibility,
            "member_policy": self.member_policy,
            "record_policy": self.record_policy,
            "owned_by": self.owned_by.dump(),
        }

    def refresh_from_dict(self, access_dict):
        """Re-initialize the Access object with the data in the access_dict."""
        new_access = self.from_dict(access_dict)
        self.visibility = new_access.visibility
        self.member_policy = new_access.member_policy
        self.record_policy = new_access.record_policy
        self.owned_by = new_access.owned_by

    @classmethod
    def from_dict(
        cls,
        access_dict,
        owners_cls=None,
    ):
        """Create a new Access object from the specified 'access' property.

        The new ``CommunityAccess`` object will be populated with new instances
        from the configured classes.
        If ``access_dict`` is empty, the ``Access`` object will be populated
        with new instance ``owners_cls``.
        """
        owners_cls = owners_cls or cls.owners_cls

        errors = []

        # provide defaults in case there is no 'access' property
        owned_by = owners_cls()

        if access_dict:
            for owner_dict in access_dict.get("owned_by", []):
                try:
                    owned_by.add(owned_by.owner_cls(owner_dict))
                except Exception as e:
                    errors.append(e)

        access = cls(
            visibility=access_dict.get("visibility"),
            member_policy=access_dict.get("member_policy"),
            record_policy=access_dict.get("record_policy"),
            owned_by=owned_by
        )
        access.errors = errors
        return access

    def __repr__(self):
        """Return repr(self)."""
        return (
            "<{} (visibility: {}, "
            "member_policy: {}, "
            "record_policy: {}, "
            "owners: {})>"
        ).format(
            type(self).__name__,
            self.visibility,
            self.member_policy,
            self.record_policy,
            self.owned_by,
        )


# TODO: Move to Invenio-Records-Resources and make reusable. Duplicated from
# Invenio-RDM-Records.
class CommunityAccessField(SystemField):
    """System field for managing record access."""

    access_obj_class = CommunityAccess

    def __init__(self, key="access", access_obj_class=None):
        """Create a new RecordAccessField instance."""
        self._access_obj_class = access_obj_class or self.access_obj_class
        super().__init__(key=key)

    def _from_dict(self, instance, data):
        """Allows to override behavior in subclass."""
        return

    def obj(self, instance):
        """Get the access object."""
        obj = self._get_cache(instance)
        if obj is not None:
            return obj

        data = self.get_dictkey(instance)
        if data:
            obj = self._access_obj_class.from_dict(data)
        else:
            obj = self._access_obj_class()

        self._set_cache(instance, obj)
        return obj

    def set_obj(self, record, obj):
        """Set the access object."""
        # We accept both dicts and access class objects.
        if isinstance(obj, dict):
            obj = self._access_obj_class.from_dict(obj)

        assert isinstance(obj, self._access_obj_class)

        # We do not dump the object until the pre_commit hook
        # I.e. record.access != record['access']
        self._set_cache(record, obj)

    def __get__(self, record, owner=None):
        """Get the record's access object."""
        if record is None:
            # access by class
            return self

        # access by object
        return self.obj(record)

    def __set__(self, record, obj):
        """Set the records access object."""
        self.set_obj(record, obj)

    def pre_commit(self, record):
        """Dump the configured values before the record is committed."""
        obj = self.obj(record)
        if obj is not None:
            # only set the 'access' property if one was present in the
            # first place -- this was a problem in the unit test:
            # tests/resources/test_resources.py:test_simple_flow
            record["access"] = obj.dump()
