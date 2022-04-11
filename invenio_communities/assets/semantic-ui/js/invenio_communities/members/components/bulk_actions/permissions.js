import _pickBy from "lodash/pickBy";

export const RolePermissionPolicy = {
  owner: "can_invite_owners",
};

export const VisibilityPermissionPolicy = {
  public: "can_update_visible",
};

export const serializeOptionsByPermissions = (options, policy, permissions) => {
  const permittedOptions = _pickBy(options, (value, key) => {
    return (key in policy && policy[key] in permissions) || !(key in policy);
  });

  return permittedOptions;
};
