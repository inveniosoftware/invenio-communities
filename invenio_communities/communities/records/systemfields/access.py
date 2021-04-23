# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Community access system field."""

from invenio_rdm_records.records.systemfields.access import Owner, Owners, \
    RecordAccessField


class _Owner(Owner):

    @property
    def user(self):
        if self.owner_type == 'user':
            return self.owner_id


class _Owners(Owners):

    owner_cls = _Owner

    def __init__(self, owners=None, owner_cls=None):
        """Create a new list of owners."""
        self.owner_cls = owner_cls or self.owner_cls
        for owner in owners or []:
            self.add(owner)


class CommunityAccess:
    """Access management per community."""

    VISIBILITY_LEVELS = ('public', 'restricted')

    owners_cls = _Owners

    def __init__(
        self,
        visibility=None,
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

        owners_cls = owners_cls or self.owners_cls
        self.owned_by = owned_by if owned_by else owners_cls()

        self.errors = []

    def _validate_visibility_level(self, level):
        return level in self.VISIBILITY_LEVELS

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

    def dump(self):
        """Dump the field values as dictionary."""
        return {
            "visibility": self.visibility,
            "owned_by": self.owned_by.dump(),
        }

    def refresh_from_dict(self, access_dict):
        """Re-initialize the Access object with the data in the access_dict."""
        new_access = self.from_dict(access_dict)
        self.visibility = new_access.visibility
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

        access = cls(visibility=access_dict["visibility"], owned_by=owned_by)
        access.errors = errors
        return access

    def __repr__(self):
        """Return repr(self)."""
        return "<{} (visibility: {}, owners: {})>".format(
            type(self).__name__,
            self.visibility,
            self.owned_by,
        )


class CommunityAccessField(RecordAccessField):
    """System field for managing community access."""

    def __init__(self, *args, access_obj_class=CommunityAccess, **kwargs):
        """Create a new CommunityAccessField instance."""
        super().__init__(*args, access_obj_class=access_obj_class, **kwargs)

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

    # NOTE: The original RecordAccessField dumps some non-existing fields
    def post_dump(self, *args, **kwargs):
        """Called before a record is dumped."""
        pass

    def pre_load(self, *args, **kwargs):
        """Called before a record is dumped."""
        pass
