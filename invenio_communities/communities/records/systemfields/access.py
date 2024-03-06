# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community access system field."""

from enum import Enum, unique

from invenio_records.systemfields import SystemField


class AccessEnumMixin:
    """Mixin for enum functionalities."""

    @classmethod
    def validate(cls, level):
        """Validate a string against the enum values."""
        return cls(level) in cls

    def __str__(self):
        """Return its value."""
        return self.value


@unique
class VisibilityEnum(AccessEnumMixin, Enum):
    """Enum defining access visibility."""

    PUBLIC = "public"

    RESTRICTED = "restricted"


@unique
class MembersVisibilityEnum(AccessEnumMixin, Enum):
    """Enum defining members visibility."""

    PUBLIC = "public"

    RESTRICTED = "restricted"


@unique
class MemberPolicyEnum(AccessEnumMixin, Enum):
    """Enum defining member policies."""

    OPEN = "open"

    CLOSED = "closed"


@unique
class RecordPolicyEnum(AccessEnumMixin, Enum):
    """Enum defining record policies."""

    OPEN = "open"

    CLOSED = "closed"


@unique
class ReviewPolicyEnum(AccessEnumMixin, Enum):
    """Enum defining review policies."""

    OPEN = "open"

    CLOSED = "closed"


class CommunityAccess:
    """Access management per community."""

    def __init__(
        self,
        visibility=None,
        members_visibility=None,
        member_policy=None,
        record_policy=None,
        review_policy=None,
    ):
        """Create a new CommunityAccess object.

        :param visibility: The visibility level.
        """
        self.visibility = visibility or VisibilityEnum.PUBLIC
        self.members_visibility = members_visibility or MembersVisibilityEnum.PUBLIC
        self.member_policy = member_policy or MemberPolicyEnum.OPEN
        self.record_policy = record_policy or RecordPolicyEnum.OPEN
        self.review_policy = review_policy or ReviewPolicyEnum.CLOSED
        self.errors = []

    @classmethod
    def validate_visibility_level(cls, level):
        """Validate the visibility level."""
        return VisibilityEnum.validate(level)

    @classmethod
    def validate_members_visibility_level(cls, level):
        """Validate the visibility level."""
        return MembersVisibilityEnum.validate(level)

    @classmethod
    def validate_member_policy_level(cls, level):
        """Validate the member policy level."""
        return MemberPolicyEnum.validate(level)

    @classmethod
    def validate_record_policy_level(cls, level):
        """Validate the record policy level."""
        return RecordPolicyEnum.validate(level)

    @classmethod
    def validate_review_policy_level(cls, level):
        """Validate the review policy level."""
        return ReviewPolicyEnum.validate(level)

    @property
    def visibility(self):
        """Get the visibility level."""
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        """Set the visibility level."""
        if not self.validate_visibility_level(value):
            raise ValueError(f"Unknown visibility level: {value}")
        self._visibility = value

    @property
    def members_visibility(self):
        """Get the members visibility level."""
        return self._members_visibility

    @members_visibility.setter
    def members_visibility(self, value):
        """Set the members visibility level."""
        if not self.validate_members_visibility_level(value):
            raise ValueError(f"Unknown members visibility level: {value}")
        self._members_visibility = value

    @property
    def visibility_is_public(self):
        """Return True when visibility is public."""
        return self.visibility == VisibilityEnum.PUBLIC.value

    @property
    def visibility_is_restricted(self):
        """Return True when visibility is restricted."""
        return self.visibility == VisibilityEnum.RESTRICTED.value

    @property
    def member_policy(self):
        """Get the member policy level."""
        return self._member_policy

    @member_policy.setter
    def member_policy(self, value):
        """Set the member policy level."""
        if not self.validate_member_policy_level(value):
            raise ValueError(f"Unknown member policy level: {value}")
        self._member_policy = value

    @property
    def record_policy(self):
        """Get the record policy level."""
        return self._record_policy

    @record_policy.setter
    def record_policy(self, value):
        """Set the record policy level."""
        if not self.validate_record_policy_level(value):
            raise ValueError(f"Unknown record policy level: {value}")
        self._record_policy = value

    @property
    def review_policy(self):
        """Get the review policy level."""
        return self._review_policy

    @review_policy.setter
    def review_policy(self, value):
        """Set the review policy level."""
        if not self.validate_review_policy_level(value):
            raise ValueError(f"Unknown review policy level: {value}")
        self._review_policy = value

    def dump(self):
        """Dump the field values as dictionary."""
        return {
            "visibility": str(self.visibility),
            "members_visibility": str(self.members_visibility),
            "member_policy": str(self.member_policy),
            "record_policy": str(self.record_policy),
            "review_policy": str(self.review_policy),
        }

    def refresh_from_dict(self, access_dict):
        """Re-initialize the Access object with the data in the access_dict."""
        new_access = self.from_dict(access_dict)
        self.visibility = new_access.visibility
        self.members_visibility = new_access.members_visibility
        self.member_policy = new_access.member_policy
        self.record_policy = new_access.record_policy
        self.review_policy = new_access.review_policy

    @classmethod
    def from_dict(
        cls,
        access_dict,
    ):
        """Create a new Access object from the specified 'access' property.

        The new ``CommunityAccess`` object will be populated with new instances
        from the configured classes.
        """
        errors = []

        access = cls(
            visibility=access_dict.get("visibility"),
            members_visibility=access_dict.get("members_visibility"),
            member_policy=access_dict.get("member_policy"),
            record_policy=access_dict.get("record_policy"),
            review_policy=access_dict.get("review_policy"),
        )
        access.errors = errors
        return access

    def __repr__(self):
        """Return repr(self)."""
        return (
            f"<{type(self).__name__} ("
            f"visibility: {str(self.visibility)}, "
            f"members_visibility: {str(self.members_visibility)}, "
            f"member_policy: {str(self.member_policy)}, "
            f"record_policy: {str(self.record_policy)}, "
            f"review_policy: {str(self.review_policy)})>"
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
