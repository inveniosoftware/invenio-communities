/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image, withCancel } from "react-invenio-forms";
import { Dropdown, Grid, Header } from "semantic-ui-react";
import _truncate from "lodash/truncate";

export class MembersSearchBar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isFetching: false,
      error: false,
      suggestions: [],
    };
  }

  serializeMemberName = (person) => {
    const name = person.profile?.full_name;

    const displayName = name
      ? `${name} <${person.email || person.username}>`
      : person.email
      ? `${person.email} <${person.username}>`
      : `<${person.username}>`;

    return displayName;
  };

  serializeUsersForDropdown = (users) => {
    const { existingEntitiesDescription } = this.props;
    // place available users on top of the list
    const sortedUsers = users.sort((a, b) => ("disabled" in a) - ("disabled" in b));
    return sortedUsers.map((person) => {
      return {
        text: person.id,
        value: person.id,
        key: person.id,
        disabled: person?.disabled,
        content: (
          <Grid textAlign="left" verticalAlign="middle" className="pt-5 pb-5">
            <Grid.Column width={1}>
              <Image size="mini" src={person.links.avatar} avatar />
            </Grid.Column>
            <Grid.Column width={9}>
              <Header as="a" className={person?.disabled ? "no-text-decoration" : ""}>
                {this.serializeMemberName(person)}
              </Header>
              <Header.Subheader>{person.profile?.affiliations}</Header.Subheader>
            </Grid.Column>
            <Grid.Column width={6}>
              {person?.disabled && <p>{existingEntitiesDescription}</p>}
            </Grid.Column>
          </Grid>
        ),
      };
    });
  };

  serializeGroupsForDropdown = (groups) => {
    const { existingEntitiesDescription } = this.props;
    // place available groups on top of the list
    const sortedGroups = groups.sort((a, b) => ("disabled" in a) - ("disabled" in b));
    return sortedGroups.map((group) => {
      return {
        text: group.id,
        value: group.id,
        key: group.id,
        disabled: group?.disabled,
        content: (
          <Grid textAlign="left" verticalAlign="middle" className="pt-5 pb-5">
            <Grid.Column width={1}>
              <Image size="mini" src={group.links.avatar} avatar />
            </Grid.Column>
            <Grid.Column width={9}>
              <Header as="a" className={group?.disabled ? "no-text-decoration" : ""}>
                {group.name}
              </Header>
              <Header.Subheader>
                {_truncate(group.description, { length: 30 })}
              </Header.Subheader>
            </Grid.Column>
            <Grid.Column width={6} textAlign="right">
              {group?.disabled && <p>{existingEntitiesDescription}</p>}
            </Grid.Column>
          </Grid>
        ),
      };
    });
  };

  optionsGenerator = (suggestions) => {
    const { searchType } = this.props;
    const serializer = {
      user: this.serializeUsersForDropdown,
    };

    if (searchType === "group") {
      serializer["group"] = this.serializeGroupsForDropdown;
    } else if (searchType === "role") {
      serializer["role"] = this.serializeGroupsForDropdown;
    }

    return serializer[searchType](suggestions);
  };

  onChange = (event, data) => {
    const { handleChange, selectedMembers, searchType } = this.props;
    const { suggestions } = this.state;

    if (data.value.length === 0) return;

    const selectedValue = data.value[0];
    const memberAlreadySelected = selectedValue in selectedMembers;

    if (memberAlreadySelected) return;

    const newSelectedMember = suggestions.find((item) => item.id === selectedValue);

    const serializedSelectedMember = {
      id: newSelectedMember.id,
      type: searchType,
      avatar: newSelectedMember?.links?.avatar,
    };

    if (searchType === "group" || searchType === "role") {
      serializedSelectedMember["name"] = newSelectedMember.name; // The schema will pass the id if the name is missing
    } else {
      serializedSelectedMember["name"] = this.serializeMemberName(newSelectedMember);
    }
    selectedMembers[serializedSelectedMember.id] = serializedSelectedMember;
    handleChange(selectedMembers);
  };

  onSearchChange = async (event, { searchQuery }) => {
    const { fetchMembers } = this.props;
    try {
      this.setState({ isFetching: true });

      const cancellableSuggestions = withCancel(fetchMembers(searchQuery));
      const suggestions = await cancellableSuggestions.promise;
      this.setState({
        isFetching: false,
        suggestions: suggestions.data.hits.hits,
        error: false,
      });
    } catch (e) {
      console.error(e);
      this.setState({
        isFetching: false,
        error: true,
      });
    }
  };

  updatedOptions = () => {
    // disable options that can not be added (members that are already added)
    const { suggestions } = this.state;
    const { existingEntities } = this.props;

    return suggestions.map((suggestion) => {
      if (existingEntities.includes(suggestion.id)) {
        return {
          ...suggestion,
          disabled: true,
        };
      }
      return suggestion;
    });
  };

  // the "search" was already done in the backend,
  // so we just return all options
  handleSearch = (options, query) => {
    return options;
  };

  render() {
    const { isFetching, error } = this.state;
    const { placeholder } = this.props;
    const options = this.updatedOptions();
    return (
      <Dropdown
        selectOnBlur={false}
        error={error}
        fluid
        loading={isFetching}
        onSearchChange={this.onSearchChange}
        onChange={this.onChange}
        search={this.handleSearch}
        options={this.optionsGenerator(options)}
        selection
        multiple
        value={[]}
        icon="search"
        placeholder={placeholder}
      />
    );
  }
}

MembersSearchBar.propTypes = {
  handleChange: PropTypes.func.isRequired,
  selectedMembers: PropTypes.object.isRequired,
  fetchMembers: PropTypes.func.isRequired,
  searchType: PropTypes.oneOf(["group", "role", "user"]).isRequired,
  placeholder: PropTypes.string,
  existingEntities: PropTypes.array.isRequired,
  existingEntitiesDescription: PropTypes.string,
};

MembersSearchBar.defaultProps = {
  placeholder: i18next.t("Search..."),
  existingEntitiesDescription: "",
};
