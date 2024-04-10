/*
 * This file is part of Invenio.
 * Copyright (C) 2024-2024 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { RadioSelection } from "@js/invenio_communities/members/components/bulk_actions/RadioSelection";
import { ErrorMessage } from "@js/invenio_communities/members/components/ErrorMessage";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Trans } from "react-i18next";
import { Button, Form, Modal } from "semantic-ui-react";
import { UsersApi } from "../../api/UsersApi";
import { MembersSearchBar } from "../invitations/invitationsModal/MemberSearchBar";
import { SelectedMembers } from "./bulk_actions/SelectedMembers";

export class SearchWithRoleSelection extends Component {
  constructor(props) {
    super(props);
    this.usersApi = new UsersApi();
    this.state = {
      role: undefined,
      selected: {},
      loading: false,
      error: undefined,
    };
  }

  updateSelected = (members) => {
    this.setState({ selected: members });
  };

  addEntityToSelected = (member) => {
    const { selected } = this.state;
    this.setState({ selected: { ...selected, ...member } });
  };

  handleRoleUpdate = (role) => {
    this.setState({ role: role });
  };

  handleActionClick = async () => {
    const { action, onSuccessCallback, message, notify } = this.props;
    const { selected, role } = this.state;
    this.setState({ loading: true, error: undefined });
    try {
      await action(selected, role, message, notify);
      this.setState({ loading: false });
      onSuccessCallback();
    } catch (error) {
      this.setState({ loading: false, error: error });
    }
  };

  render() {
    const {
      roleOptions,
      modalClose,
      searchBarTitle,
      searchBarTooltip,
      doneButtonText,
      doneButtonIcon,
      doneButtonTip,
      radioLabel,
      selectedItemsHeader,
      messageComponent,
      existingEntities,
      existingEntitiesDescription,
    } = this.props;
    const { selected, loading, error } = this.state;
    const selectedCount = Object.keys(selected).length;

    return (
      <>
        <Modal.Content className="default-padding">
          {error && <ErrorMessage error={error} />}
          <SelectedMembers
            updateSelectedMembers={this.updateSelected}
            selectedMembers={selected}
            headerText={selectedItemsHeader}
          />
          <Form>
            <Form.Field>
              {searchBarTitle}
              <MembersSearchBar
                existingEntities={existingEntities}
                existingEntitiesDescription={existingEntitiesDescription}
                fetchMembers={this.usersApi.getUsers}
                selectedMembers={selected}
                handleChange={this.addEntityToSelected}
                searchType="user"
                placeholder={i18next.t("Search by email, full name or username")}
              />
              <label className="helptext rel-mt-1">{searchBarTooltip}</label>
            </Form.Field>
            <RadioSelection
              options={roleOptions}
              label={radioLabel}
              onOptionChangeCallback={this.handleRoleUpdate}
              checked={false}
            />
            <Form.Field>{messageComponent}</Form.Field>
          </Form>
        </Modal.Content>
        <Modal.Actions>
          <Button
            content={i18next.t("Cancel")}
            labelPosition="left"
            icon="cancel"
            loading={loading}
            disabled={loading}
            floated="left"
            onClick={modalClose}
          />
          {selectedCount > 0 && (
            <Trans key="entitiesSelected" count={selectedCount}>
              {doneButtonTip} {{ selectedCount }} users
            </Trans>
          )}
          <Button
            content={doneButtonText}
            labelPosition="left"
            loading={loading}
            disabled={loading || selectedCount === 0}
            icon={doneButtonIcon}
            primary
            onClick={this.handleActionClick}
          />
        </Modal.Actions>
      </>
    );
  }
}

SearchWithRoleSelection.propTypes = {
  roleOptions: PropTypes.array.isRequired,
  modalClose: PropTypes.func.isRequired,
  action: PropTypes.func.isRequired,
  onSuccessCallback: PropTypes.func.isRequired,
  searchBarTitle: PropTypes.object,
  searchBarTooltip: PropTypes.string,
  doneButtonText: PropTypes.string,
  doneButtonIcon: PropTypes.string,
  doneButtonTip: PropTypes.string,
  radioLabel: PropTypes.string,
  selectedItemsHeader: PropTypes.string,
  message: PropTypes.string,
  messageComponent: PropTypes.object,
  notify: PropTypes.bool,
  existingEntities: PropTypes.array.isRequired,
  existingEntitiesDescription: PropTypes.string,
};

SearchWithRoleSelection.defaultProps = {
  searchBarTitle: null,
  searchBarTooltip: "",
  doneButtonText: "",
  doneButtonIcon: "",
  doneButtonTip: "",
  radioLabel: "",
  selectedItemsHeader: "",
  message: "",
  messageComponent: null,
  notify: false,
  existingEntitiesDescription: "",
};
