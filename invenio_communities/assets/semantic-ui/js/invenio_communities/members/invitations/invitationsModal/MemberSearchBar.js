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

export class MembersSearchBar extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isFetching: false,
      error: false,
      suggestions: [],
    };
  }

  serializeUsersForDropdown = (users) => {
    return users.map((person) => {
      const name = person.profile.full_name || person.id;

      return {
        text: name,
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
    const serializer = {
      user: this.serializeUsersForDropdown,
      group: this.serializeGroupsForDropdown,
    };
    return serializer[searchType](suggestions);
  };

  onChange = (event, data) => {
    const { handleChange, selectedMembers, searchType } = this.props;
    const { suggestions } = this.state;

    const memberAlreadySelected = data.value in selectedMembers;

    if (memberAlreadySelected) return;

    const newSelectedMember = suggestions.find(
      (item) => item.id === data.value
    );

    const serializedSelectedMember = {
      id: newSelectedMember.id,
      type: searchType,
      avatar_url: newSelectedMember?.links?.avatar,
    };

    serializedSelectedMember["name"] =
      newSelectedMember.profile.full_name ||
      newSelectedMember.name ||
      newSelectedMember.id;

    selectedMembers[serializedSelectedMember.id] = serializedSelectedMember;
    handleChange(selectedMembers);
  };

  onSearchChange = async (event, data) => {
    const { fetchMembers } = this.props;
    try {
      this.setState({ isFetching: true });

      const cancellableSuggestions = withCancel(fetchMembers(data.searchQuery));
      const suggestions = await cancellableSuggestions.promise;

      this.setState({
        isFetching: false,
        suggestions: suggestions.data.hits.hits,
      });
    } catch (e) {
      console.error(e);
      this.setState({
        isFetching: false,
        error: true,
      });
    }
  };

  render() {
    const { isFetching, error, suggestions } = this.state;
    const { placeholder } = this.props;
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
  handleChange: PropTypes.func.isRequired,
  selectedMembers: PropTypes.object.isRequired,
  fetchMembers: PropTypes.func.isRequired,
  searchType: PropTypes.oneOf(["group", "user"]),
  placeholder: PropTypes.string,
};

MembersSearchBar.defaultProps = {
  placeholder: i18next.t("Search ..."),
};
