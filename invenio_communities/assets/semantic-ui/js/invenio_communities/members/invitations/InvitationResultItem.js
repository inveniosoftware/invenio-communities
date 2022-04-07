/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { CommunityInvitationsApi } from "@js/invenio_communities/api/InvitationsApi";
import ActionDropdown from "../components/ActionDropdown";
import React, { Component } from "react";
import { DateTime } from "luxon";
import { Table, Container, Header } from "semantic-ui-react";
import { Image } from "react-invenio-forms";
import { ActionButtons } from "./request_actions/InvitationActionButtons";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import {
  RequestActionController,
} from "@js/invenio_requests";


const formattedTime = (expires_at) =>
  DateTime.fromISO(expires_at).setLocale(i18next.language).toRelative();

export class InvitationResultItem extends Component {
  constructor(props) {
    super(props);
    const { result } = this.props;
    this.state = { invitation: result };
    this.invitationsApi = new CommunityInvitationsApi(result.links);
  }

  updateInvitation = (data) => {
    const { invitation } = this.state;
    this.setState({ invitation: { ...invitation, ...data } });
  };

  render() {
    const {
      config: { roles },
    } = this.props;
    const {
      invitation,
      invitation: { receiver, status, expires_at, role },
    } = this.state;

    return (
      <Table.Row className="community-member-item">
        <Table.Cell>
          <Image src={"/abc"} avatar circular className="rel-mr-1" />
          <Header size="small" as="a">
            {receiver.name || receiver.user}
          </Header>
        </Table.Cell>
        <Table.Cell>{status}</Table.Cell>
        <Table.Cell>{formattedTime(expires_at)}</Table.Cell>
        <Table.Cell>
          <ActionDropdown
            options={roles}
            successCallback={this.updateInvitation}
            action={this.invitationsApi.updateRole}
            // TODO attribute missing in the invitation payload
            currentValue={role ? role : "curator"}
          />
        </Table.Cell>
        <Table.Cell>
          <Container fluid textAlign="right">
            <RequestActionController
              request={invitation}
              actionSuccessCallback={this.updateInvitation}
            >
              <ActionButtons
                request={invitation}
              />
            </RequestActionController>
          </Container>
        </Table.Cell>
      </Table.Row>
    );
  }
}

InvitationResultItem.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};

InvitationResultItem.defaultProps = {};
