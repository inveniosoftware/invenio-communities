/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { InvitationsContext } from "../../../api/invitations/InvitationsContextProvider";
import { MembersWithRoleSelection } from "./MembersWithRoleSelection";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Container, Modal, Tab } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { withState } from "react-searchkit";

import { GroupTabPane } from "./GroupTabPane";

export class InvitationsMembersModal extends Component {
  static contextType = InvitationsContext;

  constructor(props) {
    super(props);
    this.state = {
      open: false,
    };
  }

  onSuccess = () => {
    const { updateQueryState, currentQueryState } = this.props;
    updateQueryState(currentQueryState);
    this.handleCloseModal();
  };

  getPanes = () => {
    const { allowGroups, roles } = this.props;
    const { api } = this.context;
    const peopleTab = {
      menuItem: i18next.t("People"),
      pane: (
        <Tab.Pane key="members-users" as={Container}>
          <MembersWithRoleSelection
            key="members-users"
            roleOptions={roles}
            modalClose={this.handleCloseModal}
            action={api.createInvite}
            onSuccessCallback={this.onSuccess}
          />
        </Tab.Pane>
      ),
    };

    const groupsTab = {
      menuItem: i18next.t("Groups"),
      pane: (
        <Tab.Pane key="members-groups" as={Container}>
          <GroupTabPane
            modalClose={this.handleCloseModal}
            roleOptions={roles}
            action={api.createInvite}
            onSuccessCallback={this.onSuccess}
          />
        </Tab.Pane>
      ),
      action: { label: i18next.t("Invite groups") },
    };
    return allowGroups ? [peopleTab, groupsTab] : [peopleTab];
  };

  handleCloseModal = () => this.setState({ open: false });

  handleOpenModal = () => this.setState({ open: true });

  render() {
    const { open } = this.state;
    return (
      <Modal
        onClose={this.handleCloseModal}
        onOpen={this.handleOpenModal}
        closeOnDimmerClick={false}
        open={open}
        trigger={
          <Button
            content={i18next.t("Invite members")}
            positive
            size="medium"
            className="ml-5"
          />
        }
      >
        <Modal.Header>{i18next.t("Invite members")}</Modal.Header>
        <Tab
          menu={{
            className: "rel-pl-2 rel-pt-2",
            tabular: true,
          }}
          panes={this.getPanes()}
          renderActiveOnly={false}
        />
      </Modal>
    );
  }
}

InvitationsMembersModal.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  roles: PropTypes.object.isRequired,
  allowGroups: PropTypes.bool.isRequired,
};

export const InvitationsMembersModalWithSearchKit = withState(
  InvitationsMembersModal
);
