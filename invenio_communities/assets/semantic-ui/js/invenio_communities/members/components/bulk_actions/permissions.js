import _pickBy from "lodash/pickBy";

export const RolePermissionPolicy = {
  owner: "can_invite_owners",
};

export const VisibilityPermissionPolicy = {
  public: "can_update_visible",
};

export const filterOptionsByPermissions = (options, policy, permissions) => {
  return options.filter(({ name }) => {
    return (name in policy && policy[name] in permissions) || !(name in policy);
  });
};
