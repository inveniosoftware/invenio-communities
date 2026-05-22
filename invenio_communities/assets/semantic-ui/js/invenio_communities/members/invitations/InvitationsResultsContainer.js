/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import PropTypes from "prop-types";
import { Table } from "semantic-ui-react";
import { InvitationsContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { InvitationsMembersModalWithSearchKit } from "./invitationsModal/InvitationsMembersModal";
import Overridable from "react-overridable";

export const InvitationsResultsContainer = ({
  results,
  rolesCanInvite,
  community,
  groupsEnabled,
}) => {
  return (
    <Table>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell width={6}>{i18next.t("Name")}</Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Status")}</Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Expires")}</Table.HeaderCell>
          <Table.HeaderCell width={3}>{i18next.t("Role")}</Table.HeaderCell>
          <Table.HeaderCell width={1} textAlign="right">
            <InvitationsContextProvider community={community}>
              <Overridable
                id="InvenioCommunities.CommunityMembersSearch.InvitationsResultsContainer.InvitationsModal.container"
                rolesCanInvite={rolesCanInvite}
                groupsEnabled={groupsEnabled}
                community={community}
              >
                <InvitationsMembersModalWithSearchKit
                  rolesCanInvite={rolesCanInvite}
                  groupsEnabled={groupsEnabled}
                  community={community}
                  triggerButtonSize="tiny"
                />
              </Overridable>
            </InvitationsContextProvider>
          </Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>{results}</Table.Body>
    </Table>
  );
};

InvitationsResultsContainer.propTypes = {
  results: PropTypes.array.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  groupsEnabled: PropTypes.bool.isRequired,
};
