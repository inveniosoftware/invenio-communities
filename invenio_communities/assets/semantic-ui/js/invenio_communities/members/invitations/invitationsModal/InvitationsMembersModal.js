/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2024 CERN.
 * Copyright (C) 2024      KTH Royal Institute of Technology.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { InvenioCommunitiesRoutesGenerator } from "../../../routes/appUrls";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { withState } from "react-searchkit";
import { Button, Container, Modal, Tab } from "semantic-ui-react";
import { InvitationsContext } from "../../../api/invitations/InvitationsContextProvider";
import { GroupTabPane } from "./GroupTabPane";
import { SearchWithRoleSelection } from "../../components/SearchWithRoleSelection";
import { RichEditor, withCancel, http } from "react-invenio-forms";
import { UsersApi } from "../../../api";

export class InvitationsMembersModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      activeIndex: 0, // by default members is the active pane
      message: undefined,
      existingIds: [],
    };
  }

  static contextType = InvitationsContext;

  onMemberSuccess = () => {
    const { updateQueryState, currentQueryState } = this.props;
    updateQueryState(currentQueryState);
    this.handleCloseModal();
  };

  updateMessage = (message) => {
    this.setState({ message: message });
  };

  onGroupSuccess = () => {
    const { community } = this.props;
    window.location = InvenioCommunitiesRoutesGenerator.membersList(community.slug);
  };

  fetchExisting = async () => {
    // merge all open invitations and members to grey them out in the search
    const { community } = this.props;
    this.cancellableAction = withCancel(
      http.get(`${community.links.invitations}?is_open=true`)
    );
    const invitationsResponse = await this.cancellableAction.promise;
    const invitations = invitationsResponse?.data?.hits?.hits;

    this.cancellableAction = withCancel(http.get(community.links.members));
    const membersResponse = await this.cancellableAction.promise;
    const members = membersResponse?.data?.hits?.hits;

    const existing = [...invitations, ...members];

    const existingEntitiesIds = [];
    existing.forEach((result) => {
      existingEntitiesIds.push(result?.member?.id);
    });

    this.setState({
      existingIds: existingEntitiesIds,
    });
  };

  getPanes = () => {
    const { groupsEnabled, rolesCanInvite, community } = this.props;
    const { activeIndex, message, existingIds } = this.state;
    const { api } = this.context;
    const userRoles = rolesCanInvite["user"];
    const client = new UsersApi();

    const peopleTab = {
      menuItem: (
        <Button
          role="tab"
          className="item"
          id="members-users-tab"
          aria-controls="members-users-tab-panel"
          aria-selected={activeIndex === 0}
        >
          {i18next.t("People")}
        </Button>
      ),
      pane: (
        <Tab.Pane
          role="tabpanel"
          id="members-users-tab-panel"
          aria-labelledby="members-users-tab"
          key="members-users"
          as={Container}
        >
          <SearchWithRoleSelection
            key="members-users"
            searchType="user"
            fetchMembers={client.suggestUsers}
            roleOptions={userRoles}
            modalClose={this.handleCloseModal}
            action={api.createInvite}
            onSuccessCallback={this.onMemberSuccess}
            searchBarTitle={<label>{i18next.t("Member")}</label>}
            searchBarTooltip={i18next.t(
              "Search for users to invite (only users with a public profile can be invited)"
            )}
            doneButtonText={i18next.t("Invite")}
            doneButtonIcon="checkmark"
            radioLabel={i18next.t("Role")}
            selectedItemsHeader={i18next.t("No selected members")}
            message={message}
            messageComponent={
              <>
                <label>{i18next.t("Invitation message")}</label>
                <RichEditor
                  inputValue={() => message} // () => Needed to avoid re-rendering
                  onBlur={(event, editor) => {
                    this.updateMessage(editor.getContent());
                  }}
                />
              </>
            }
            doneButtonTip={i18next.t("You are about to invite")}
            doneButtonTipType={i18next.t("users")}
            existingEntities={existingIds}
            existingEntitiesDescription={i18next.t(
              "Already a member or invitation pending"
            )}
            searchBarPlaceholder={i18next.t("Search by email, full name or username")}
          />
        </Tab.Pane>
      ),
    };

    const groupRoles = rolesCanInvite["group"];
    const groupsTab = {
      menuItem: (
        <Button
          role="tab"
          className="item"
          id="members-group-tab"
          aria-controls="members-groups-tab-panel"
          aria-selected={activeIndex === 1}
        >
          {i18next.t("Groups")}
        </Button>
      ),
      pane: (
        <Tab.Pane
          role="tabpanel"
          id="members-groups-tab-panel"
          aria-labelledby="members-groups-tab"
          key="members-groups"
          as={Container}
        >
          <GroupTabPane
            modalClose={this.handleCloseModal}
            roleOptions={groupRoles}
            action={api.addGroupToMembers}
            onSuccessCallback={this.onGroupSuccess}
            community={community}
          />
        </Tab.Pane>
      ),
      action: { label: i18next.t("Invite groups") },
    };
    return groupsEnabled ? [peopleTab, groupsTab] : [peopleTab];
  };

  handleCloseModal = () => this.setState({ open: false });

  handleOpenModal = () => {
    this.fetchExisting();
    this.setState({ open: true }, () => {
      const membersTab = document.getElementById("members-users-tab");
      membersTab.focus();
    });
  };

  handleTabChange = (e, { activeIndex }) => this.setState({ activeIndex });

  render() {
    const { open, activeIndex } = this.state;
    const { triggerButtonSize } = this.props;
    return (
      <Modal
        role="dialog"
        onClose={this.handleCloseModal}
        onOpen={this.handleOpenModal}
        closeOnDimmerClick={false}
        open={open}
        aria-label={i18next.t("Invite members")}
        trigger={
          <Button
            className="fluid-responsive"
            content={i18next.t("Invite...")}
            positive
            fluid
            compact
            size={triggerButtonSize}
            icon="user plus"
            labelPosition="left"
            aria-expanded={open}
            aria-haspopup="dialog"
          />
        }
      >
        <Modal.Header as="h2">
          {activeIndex === 0 ? i18next.t("Invite members") : i18next.t("Add groups")}
        </Modal.Header>
        <Tab
          menu={{
            className: "rel-pl-2 rel-pt-2",
            tabular: true,
            role: "tablist",
          }}
          activeIndex={activeIndex}
          panes={this.getPanes()}
          renderActiveOnly={false}
          onTabChange={this.handleTabChange}
        />
      </Modal>
    );
  }
}

InvitationsMembersModal.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  groupsEnabled: PropTypes.bool.isRequired,
  community: PropTypes.object.isRequired,
  triggerButtonSize: PropTypes.string,
};

InvitationsMembersModal.defaultProps = {
  triggerButtonSize: "medium",
};

export const InvitationsMembersModalWithSearchKit = withState(InvitationsMembersModal);
