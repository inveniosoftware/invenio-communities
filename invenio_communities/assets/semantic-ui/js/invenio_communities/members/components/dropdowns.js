import React from "react";
import ActionDropdown from "./ActionDropdown";
import { Item, List } from "semantic-ui-react";
import PropTypes from "prop-types";

const rolesToDropdownOptions = (roles) =>
  roles.map((role) => ({
    key: role.name,
    text: role.title,
    value: role.name,
    content: (
      <List>
        <List.Item>
          <List.Content>
            <List.Header>{role.title}</List.Header>
            <List.Description>{role.description}</List.Description>
          </List.Content>
        </List.Item>
      </List>
    ),
  }));

export const RoleDropdown = ({
  roles,
  successCallback,
  action,
  disabled,
  currentValue,
  resource,
}) => {
  return (
    <ActionDropdown
      optionsSerializer={rolesToDropdownOptions}
      options={roles}
      successCallback={successCallback}
      action={action}
      disabled={disabled}
      currentValue={currentValue}
      resource={resource}
    />
  );
};

RoleDropdown.propTypes = {
  ...ActionDropdown.propTypes,
  roles: PropTypes.array.isRequired,
};

const visibilityTypesToDropdownOptions = (options) => {
  return options.map((settings) => {
    return {
      key: settings.name,
      text: settings.title,
      value: settings.visible,
      content: (
        <Item.Group>
          <Item className="members-dropdown-option">
            <Item.Content>
              <Item.Description>
                <strong>{settings.title}</strong>
              </Item.Description>
              <Item.Meta>{settings.description}</Item.Meta>
            </Item.Content>
          </Item>
        </Item.Group>
      ),
    };
  });
};

export const VisibilityDropdown = ({
  visibilityTypes,
  successCallback,
  action,
  disabled,
  currentValue,
  resource,
}) => {
  return (
    <ActionDropdown
      optionsSerializer={visibilityTypesToDropdownOptions}
      options={visibilityTypes}
      successCallback={successCallback}
      action={action}
      disabled={disabled}
      currentValue={currentValue}
      resource={resource}
    />
  );
};

VisibilityDropdown.propTypes = {
  ...ActionDropdown.propTypes,
  visibilityTypes: PropTypes.array.isRequired,
};
