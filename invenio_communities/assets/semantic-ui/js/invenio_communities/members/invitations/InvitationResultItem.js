/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { InvitationsContext } from "../../api/invitations/InvitationsContextProvider";
import React, { Component } from "react";
import { DateTime } from "luxon";
import { Container, Header, Table } from "semantic-ui-react";
import { Image } from "react-invenio-forms";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { RoleDropdown } from "../components/dropdowns";

const formattedTime = (expires_at) =>
  DateTime.fromISO(expires_at).setLocale(i18next.language).toRelative();

export class InvitationResultItem extends Component {
  static contextType = InvitationsContext;

  constructor(props) {
    super(props);
    const { result } = this.props;
    this.state = { invitation: result };
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
      invitation: { member, status, expires_at, role, permissions },
    } = this.state;
    const { api: invitationsApi } = this.context;

    return (
      <Table.Row className="community-member-item">
        <Table.Cell>
          <Image src={member.avatar_url} avatar circular className="rel-mr-1" />
          <Header size="small" as="b">
            {member.name}
          </Header>
        </Table.Cell>
        <Table.Cell>{status}</Table.Cell>
        <Table.Cell>{formattedTime(expires_at)}</Table.Cell>
        <Table.Cell>
          <RoleDropdown
            roles={roles}
            successCallback={this.updateInvitation}
            action={invitationsApi.updateRole}
            disabled={!permissions.can_update_role}
            currentValue={role}
            resource={invitation}
          />
        </Table.Cell>
        <Table.Cell>
          <Container fluid textAlign="right">
            {/* TODO uncomment when links available in the request resource subschema */}
            {/*<RequestActionController*/}
            {/*  request={invitation.request }*/}
            {/*  actionSuccessCallback={this.updateInvitation}*/}
            {/*>*/}
            {/*<ActionButtons request={invitation} />*/}
            {/*</RequestActionController>*/}
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
