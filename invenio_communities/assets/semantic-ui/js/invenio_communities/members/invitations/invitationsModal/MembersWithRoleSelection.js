/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { ErrorMessage } from "@js/invenio_communities/members/components/ErrorMessage";
import { RadioSelection } from "@js/invenio_communities/members/components/bulk_actions/RadioSelection";
import { SelectedMembers } from "../../components/bulk_actions/SelectedMembers";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Form, Modal } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { Trans } from "react-i18next";
import { MembersSearchBar } from "./MemberSearchBar";
import ClassicEditor from "@ckeditor/ckeditor5-build-classic";
import CKEditor from "@ckeditor/ckeditor5-react";
import { UsersApi } from "../../../api/UsersApi";

export class MembersWithRoleSelection extends Component {
  constructor(props) {
    super(props);
    this.usersApi = new UsersApi();
    this.state = {
      role: undefined,
      selectedMembers: {},
      message: undefined,
      loading: false,
      error: undefined,
    };
  }

  updateSelectedMembers = (members) => {
    this.setState({ selectedMembers: members });
  };

  addMemberToSelected = (member) => {
    const { selectedMembers } = this.state;
    this.setState({ selectedMembers: { ...selectedMembers, ...member } });
  };

  handleRoleUpdate = (role) => {
    this.setState({ role: role });
  };

  updateMessage = (message) => {
    this.setState(message);
  };

  handleActionClick = async () => {
    const { action, onSuccessCallback } = this.props;
    const { selectedMembers, role, message } = this.state;
    this.setState({ loading: true });
    try {

      await action(selectedMembers, role, message);
      onSuccessCallback();
    } catch (error) {
      this.setState({ loading: false, error: error });
    }
  };

  render() {
    const { roleOptions, modalClose } = this.props;
    const { selectedMembers, loading, error } = this.state;
    const selectedCount = Object.keys(selectedMembers).length;

    return (
      <>
        <div className="rel-pl-2 rel-pr-2 rel-pb-2 rel-pt-2">
          {error && <ErrorMessage error={error} />}
          <SelectedMembers
            updateSelectedMembers={this.updateSelectedMembers}
            selectedMembers={selectedMembers}
            displayingGroups={false}
          />
          <Form>
            <Form.Field>
              <label>{i18next.t("Member")}</label>
              <MembersSearchBar
                fetchMembers={this.usersApi.getUsers}
                selectedMembers={selectedMembers}
                handleChange={this.addMemberToSelected}
                searchType="user"
                placeholder={i18next.t(
                  "Search by email, full name or username"
                )}
              />
            </Form.Field>
            <RadioSelection
              options={roleOptions}
              label={i18next.t("Role")}
              onOptionChangeCallback={this.handleRoleUpdate}
            />
            <Form.Field>
              <>
                <label>{i18next.t("Message")}</label>
                <CKEditor
                  editor={ClassicEditor}
                  onBlur={(event, editor) => {
                    this.updateMessage(editor.getData());
                  }}
                />
              </>
            </Form.Field>
          </Form>
        </div>
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
            <Trans key="communityInviteMembersSelected" count={selectedCount}>
              You are about to invite {{ selectedCount }} users
            </Trans>
          )}
          <Button
            content={i18next.t("Invite")}
            labelPosition="left"
            loading={loading}
            disabled={loading || selectedCount === 0}
            icon="checkmark"
            primary
            onClick={this.handleActionClick}
          />
        </Modal.Actions>
      </>
    );
  }
}

MembersWithRoleSelection.propTypes = {
  roleOptions: PropTypes.object.isRequired,
  modalClose: PropTypes.func.isRequired,
};

MembersWithRoleSelection.defaultProps = {};
