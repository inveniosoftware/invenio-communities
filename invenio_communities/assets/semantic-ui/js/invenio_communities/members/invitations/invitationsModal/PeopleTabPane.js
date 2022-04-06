/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Tab, Form, Item } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import _isEmpty from "lodash/isEmpty";
import { MembersSearchBar } from "./MemberSearchBar";
import ClassicEditor from "@ckeditor/ckeditor5-build-classic";
import CKEditor from "@ckeditor/ckeditor5-react";
import { UsersApi } from "../../../api/UsersApi";

export class PeopleTabPane extends Component {
  render() {
    const {
      selectedMembers,
      suggestions,
      updateSuggestions,
      updateSelectedMembers,
      updateMessage,
      roleOptions,
    } = this.props;
    const client = new UsersApi();
    return (
      <Tab.Pane className="pl-30 pr-30">
        <Form>
          <Form.Field>
            <label>{i18next.t("Member")}</label>
            <MembersSearchBar
              fetchMembers={client.getUsers}
              selectedMembers={selectedMembers}
              suggestions={suggestions}
              handleChange={updateSelectedMembers}
              handleSearchChange={updateSuggestions}
              searchType="user"
              placeholder={i18next.t("Search by email, full name or username")}
            />
          </Form.Field>
          <Form.Field required>
            <label>{i18next.t("Role")}</label>
            <Item.Group className="mt-10">{roleOptions}</Item.Group>
          </Form.Field>

          <Form.Field>
            <label>{i18next.t("Message")}</label>
            <CKEditor
              editor={ClassicEditor}
              onBlur={(event, editor) => {
                updateMessage(editor.getData());
              }}
            />
          </Form.Field>
        </Form>
      </Tab.Pane>
    );
  }
}

PeopleTabPane.propTypes = {
  selectedMembers: PropTypes.array.isRequired,
  updateSelectedMembers: PropTypes.func.isRequired,
  updateSuggestions: PropTypes.func.isRequired,
  updateMessage: PropTypes.func.isRequired,
  suggestions: PropTypes.array.isRequired,
  roleOptions: PropTypes.node.isRequired,
};
