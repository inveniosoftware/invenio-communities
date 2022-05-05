/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

/*
 * To set a PermissionPolicy we need to do it in the following format:
 * {
 *  <permission_plicy>: <array_of_id>
 * }
 * if the permission policy that is defined is not part of the permissions
 * then we will filter only the values with the id we set in the array.
 */

export const RolePermissionPolicy = {
  can_invite_owners: ["manager", "curator", "reader"],
};

export const filterOptionsByPermissions = (options, policy, permissions) => {
  if (Object.keys(policy).length != 1) {
    throw 'PermissionPolicy object must contain only 1 pair "key, value"';
  }
  for (const [key, value] of Object.entries(policy)) {
    if (permissions[key]) {
      return options;
    } else {
      return options.filter(({ name }) => value.includes(name));
    }
  }
};
