# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Communities is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Registry and definition of community roles."""


from dataclasses import dataclass, field


@dataclass(frozen=True)
class Role:
    """Role class."""

    name: str = ""
    """Name of the role."""

    title: str = ""
    """Title of the role."""

    description: str = ""
    """Brief description of capabilities of the role."""

    can_manage_roles: list = field(default_factory=list)
    """List of other roles that this role can manage."""

    is_owner: bool = False
    """This role is the owner role (only one can exists)."""

    can_manage: bool = False
    """This role has manage permissions."""

    can_curate: bool = False
    """This role has record manage permissions."""

    can_view: bool = False
    """This role has view restricted record permissions."""

    def can_manage_role(self, role_name):
        """Determine if this role can manage the role name."""
        return role_name in self.can_manage_roles

    def __hash__(self):
        """Compute a hash for use with e.g. sets."""
        return self.name.__hash__()


class RoleRegistry:
    """Registry of community roles."""

    def __init__(self, roles_definitions):
        """Initialize the role registry."""
        self._roles = [Role(**role) for role in roles_definitions]

        self._owner = None

        for r in self._roles:
            if r.is_owner:
                assert self._owner is None, "Only one role be defined as owner."
                self._owner = r
        assert self._owner is not None, "One role must be defined as owner."

    def __contains__(self, key):
        """Determine if key is a valid role id."""
        for role in self._roles:
            if key == role.name:
                return True
        return False

    def __getitem__(self, key):
        """Get a role for a specific key."""
        for role in self._roles:
            if key == role.name:
                return role
        raise KeyError(key)

    def __iter__(self):
        """Iterate list of roles."""
        return iter(self.roles)

    @property
    def roles(self):
        """Get a list of roles."""
        return self._roles

    @property
    def owner_role(self):
        """Get the owner role."""
        return self._owner

    def can(self, action):
        """Returns the roles that can do the action."""
        for role in self.roles:
            if getattr(role, f"can_{action}"):
                yield role

    def manager_roles(self, role_name):
        """Get all roles that can manage members a given role.

        A manager can manage other managers, curators and readers.
        An owner can manage other owners, managers, curators and readers.

        This is used for instance to ensure that a manager cannot invite an
        owner and thereby escalate their privileges.
        """
        allowed_roles = []

        for role in self.roles:
            if role.can_manage_role(role_name):
                allowed_roles.append(role)
        return allowed_roles
