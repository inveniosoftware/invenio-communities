/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import { Component, default as React, default as React } from "react";
import { Image } from "react-invenio-forms";
import { Container, Grid, Item, Table } from "semantic-ui-react";
import { InvitationsContext } from "../../api/invitations/InvitationsContextProvider";
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

  updateInvitation = (data, value) => {
    const { invitation } = this.state;
    this.setState({ invitation: { ...invitation, ...{ role: value } } });
  };

  render() {
    const {
      config: { roles },
      community,
    } = this.props;
    const { invitation } = this.state;
    const { api: invitationsApi } = this.context;

    return (
      <Table.Row className="community-member-item">
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex" key={invitation.id}>
                <Image
                  src={invitation.member.avatar_url}
                  avatar
                  circular
                  className="rel-mr-1"
                />
                <Item.Content className="ml-10">
                  <Item.Header size="small" as="b">
                    <a
                      href={`/communities/${community.slug}/requests/${invitation.request.id}`}
                    >
                      {invitation.member.name}
                    </a>
                  </Item.Header>
                  {invitation.member.description && (
                    <Item.Meta>
                      <div
                        className="truncate-lines-1"
                        dangerouslySetInnerHTML={{
                          __html: invitation.member.description,
                        }}
                      />
                    </Item.Meta>
                  )}
                </Item.Content>
              </Item>
            </Grid.Column>
          </Grid>
        </Table.Cell>
        <Table.Cell>{invitation.request.status}</Table.Cell>
        <Table.Cell>{formattedTime(invitation.request.expires_at)}</Table.Cell>
        <Table.Cell>
          <RoleDropdown
            roles={roles}
            successCallback={this.updateInvitation}
            action={invitationsApi.updateRole}
            disabled={!invitation.permissions.can_update_role}
            currentValue={invitation.role}
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
