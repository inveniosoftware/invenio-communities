/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { List, Dropdown } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { Image, withCancel } from "react-invenio-forms";
import _isEmpty from "lodash/isEmpty";

export class MembersSearchBar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isFetching: false,
      error: false,
    };
  }

  serializeUsersForDropdown = (users) => {
    return users.map((person) => {
      const name = person.profile.full_name
        ? person.profile.full_name
        : person.id;
      return {
        text: person.profile.full_name,
        value: person.id,
        key: person.id,
        content: (
          <List divided relaxed>
            <List.Item>
              <Image size="mini" src={person.links.avatar} avatar />
              <List.Content>
                <List.Header as="a">{name}</List.Header>
                <List.Description>
                  {person.profile.affiliations}
                </List.Description>
              </List.Content>
            </List.Item>
          </List>
        ),
      };
    });
  };

  serializeGroupsForDropdown = (groups) => {
    return groups.map((group) => {
      return {
        text: group.name,
        value: group.id,
        key: group.id,
        content: (
          <List divided relaxed>
            <List.Item>
              <Image size="mini" src={group.links.avatar} avatar />
              <List.Content>
                <List.Header as="a">{group.name}</List.Header>
              </List.Content>
            </List.Item>
          </List>
        ),
      };
    });
  };

  optionsGenerator = (suggestions) => {
    const { searchType } = this.props;
    if (searchType === "user") {
      return this.serializeUsersForDropdown(suggestions);
    } else if (searchType === "group") {
      return this.serializeGroupsForDropdown(suggestions);
    }
  };

  onChange = (event, data) => {
    const { handleChange, selectedMembers, suggestions, searchType } =
      this.props;
    if (
      !selectedMembers.some(
        (member) => member.id === data.value && member.type === searchType
      )
    ) {
      const newSelectedMember = suggestions.find(
        (item) => item.id === data.value
      );
      const serializedSelectedMember = {
        id: newSelectedMember.id,
        type: searchType,
        avatar: newSelectedMember.links.avatar,
      };
      if (searchType === "user") {
        serializedSelectedMember["name"] = newSelectedMember.profile.full_name
          ? newSelectedMember.profile.full_name
          : newSelectedMember.id;
      } else if (searchType === "group") {
        serializedSelectedMember["name"] = newSelectedMember.name;
      }
      selectedMembers.push(serializedSelectedMember);
      handleChange(selectedMembers);
    }
  };

  onSearchChange = async (event, data) => {
    const { handleSearchChange, fetchMembers } = this.props;
    try {
      this.setState({ isFetching: true });
      const cancellableSuggestions = withCancel(fetchMembers(data.searchQuery));
      const suggestions = await cancellableSuggestions.promise;
      this.setState({
        isFetching: false,
      });
      handleSearchChange(suggestions.data.hits.hits);
    } catch (e) {
      console.error(e);
      this.setState({
        isFetching: false,
        error: true,
      });
    }
  };

  render() {
    const { isFetching, error } = this.state;
    const { suggestions, placeholder } = this.props;
    return (
      <Dropdown
        selectOnBlur={false}
        error={error}
        fluid
        loading={isFetching}
        onSearchChange={this.onSearchChange}
        onChange={this.onChange}
        search
        options={this.optionsGenerator(suggestions)}
        selection
        value=""
        icon="search"
        placeholder={placeholder}
      />
    );
  }
}

MembersSearchBar.propTypes = {
  handleSearchChange: PropTypes.func.isRequired,
  handleChange: PropTypes.func.isRequired,
  selectedMembers: PropTypes.array.isRequired,
  suggestions: PropTypes.array.isRequired,
  fetchMembers: PropTypes.func.isRequired,
  searchType: PropTypes.oneOf(["group", "user"]),
  placeholder: PropTypes.string,
};

MembersSearchBar.defaultProps = {
  placeholder: i18next.t("Search ..."),
};
