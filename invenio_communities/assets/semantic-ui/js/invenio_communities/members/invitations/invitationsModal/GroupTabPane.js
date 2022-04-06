/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Tab, Form, Item, Header } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import _isEmpty from "lodash/isEmpty";
import { MembersSearchBar } from "./MemberSearchBar";
import { GroupsApi } from "../../../api/GroupsApi";

export class GroupTabPane extends Component {
  render() {
    const {
      selectedMembers,
      suggestions,
      updateSuggestions,
      updateSelectedMembers,
      roleOptions,
    } = this.props;
    const client = new GroupsApi();
    return (
      <Tab.Pane className="pl-30 pr-30">
        <Form>
          <Form.Field>
            <label>{i18next.t("Group")}</label>
            <MembersSearchBar
              fetchMembers={client.getGroups}
              selectedMembers={selectedMembers}
              suggestions={suggestions}
              handleChange={updateSelectedMembers}
              handleSearchChange={updateSuggestions}
              searchType="group"
              placeholder={i18next.t("Search for groups")}
            />
          </Form.Field>
          <Form.Field required>
            <label>{i18next.t("Role")}</label>
            <Item.Group className="mt-10">{roleOptions}</Item.Group>
          </Form.Field>
        </Form>
      </Tab.Pane>
    );
  }
}

GroupTabPane.propTypes = {
  selectedMembers: PropTypes.array.isRequired,
  updateSelectedMembers: PropTypes.func.isRequired,
  updateSuggestions: PropTypes.func.isRequired,
  suggestions: PropTypes.array.isRequired,
  roleOptions: PropTypes.node.isRequired,
};
