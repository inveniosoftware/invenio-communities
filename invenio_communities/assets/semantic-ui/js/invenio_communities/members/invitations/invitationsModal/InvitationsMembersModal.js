/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  Button,
  Modal,
  Tab,
  Form,
  Checkbox,
  Item,
} from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import _isEmpty from "lodash/isEmpty";
import { withState } from "react-searchkit";
import _upperFirst from "lodash/get";
import { CommunityInvitationsApi } from "../../../api";
import { ErrorMessage } from "../../components/ErrorMessage";
import { SelectedMembers } from "./SelectedMembers";

import { PeopleTabPane } from "./PeopleTabPane";
import { GroupTabPane } from "./GroupTabPane";

export class InvitationsMembersModal extends Component {
  constructor(props) {
    super(props);

    this.state = {
      open: false,
      selectedMembers: [],
      role: undefined,
      message: "",
      error: undefined,
      isLoading: false,
      suggestions: [],
    };
  }

  inviteMembers = async () => {
    const { communityID, updateQueryState, currentQueryState } = this.props;
    const { selectedMembers, role, message } = this.state;
    const client = new CommunityInvitationsApi();
    const serializedMembers = selectedMembers.map((member) => {
      return { type: member.type, id: member.id };
    });
    const payload = {
      members: serializedMembers,
      role: role,
      message: message,
    };
    try {
      this.setState({ isLoading: true });
      await client.createInvite(communityID, payload);
      // TODO: Remove the timeout once the check to see if it was indexed in ES is implemented in the backend
      await new Promise((resolve) => setTimeout(resolve, 2000));
      updateQueryState(currentQueryState);
      this.setState({
        open: false,
        isLoading: false,
        selectedMembers: [],
        role: undefined,
        message: "",
        suggestions: [],
        error: undefined,
      });
    } catch (e) {
      this.setState({ error: e.response.data, isLoading: false });
    }
  };

  roleOptions = () => {
    const { roles } = this.props;
    const { role } = this.state;

    return Object.entries(roles).map(([key, value]) => (
      <Item>
        <Item.Content>
          <Item.Header>
            <Form.Field>
              <Checkbox
                radio
                onClick={() => this.setState({ role: key })}
                label={value.title}
                name={value.title}
                value={key}
                checked={role === key}
              />
            </Form.Field>
          </Item.Header>
          <Item.Meta className="ml-25 mt-0">{value.description}</Item.Meta>
        </Item.Content>
      </Item>
    ));
  };

  getPanes = () => {
    const { selectedMembers, suggestions } = this.state;
    const { allowGroups } = this.props;
    const peopleTab = {
      menuItem: i18next.t("People"),
      render: () => (
        <PeopleTabPane
          selectedMembers={selectedMembers}
          updateSuggestions={this.updateSuggestions}
          updateSelectedMembers={this.updateSelectedMembers}
          updateMessage={this.updateMessage}
          suggestions={suggestions}
          roleOptions={this.roleOptions()}
        />
      ),
    };

    const groupsTab = {
      menuItem: i18next.t("Groups"),
      render: () => (
        <GroupTabPane
          selectedMembers={selectedMembers}
          updateSuggestions={this.updateSuggestions}
          updateSelectedMembers={this.updateSelectedMembers}
          suggestions={suggestions}
          roleOptions={this.roleOptions()}
        />
      ),
    };
    return allowGroups ? [peopleTab, groupsTab] : [peopleTab];
  };

  updateSelectedMembers = (selectedMembers) => {
    this.setState({ selectedMembers: selectedMembers });
  };

  updateSuggestions = (suggestions) => {
    this.setState({ suggestions: suggestions });
  };

  updateMessage = (newMessage) => {
    this.setState({ message: newMessage });
  };

  render() {
    const { isLoading, open, selectedMembers, error } = this.state;
    return (
      <Modal
        onClose={() =>
          this.setState({
            open: false,
          })
        }
        onOpen={() =>
          this.setState({
            open: true,
          })
        }
        closeOnDimmerClick={false}
        open={open}
        className="invite-members-modal"
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
        <Modal.Content className="pl-0 pr-0 pb-0">
          {error && <ErrorMessage error={error} />}
          <SelectedMembers
            updateSelectedMembers={this.updateSelectedMembers}
            selectedMembers={selectedMembers}
          />
          <Tab
            onTabChange={() => this.setState({ suggestions: [] })}
            menu={{ className: "pl-30", attached: true, tabular: true }}
            panes={this.getPanes()}
          />
        </Modal.Content>
        <Modal.Actions>
          <Button
            content={i18next.t("Cancel")}
            labelPosition="left"
            icon="cancel"
            loading={isLoading}
            disabled={isLoading}
            floated="left"
            onClick={() =>
              this.setState({
                open: false,
                error: null,
              })
            }
          />
          <Button
            content={i18next.t("Invite")}
            labelPosition="left"
            loading={isLoading}
            disabled={isLoading}
            icon="checkmark"
            onClick={() => this.inviteMembers()}
            primary
          />
        </Modal.Actions>
      </Modal>
    );
  }
}

InvitationsMembersModal.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  roles: PropTypes.object.isRequired,
  communityID: PropTypes.string.isRequired,
  allowGroups: PropTypes.bool.isRequired,
};

export const InvitationsMembersModalWithState = withState(
  InvitationsMembersModal
);
