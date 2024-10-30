/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import RequestStatus from "@js/invenio_requests/request/RequestStatus";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { Grid, Item, Table } from "semantic-ui-react";

import { MembershipRequestsContext } from "../../api/membershipRequests/MembershipRequestsContextProvider";
import { RoleDropdown } from "../components/dropdowns";
import { buildRequest, formattedTime } from "../utils";

export class MembershipRequestsResultItem extends Component {
  constructor(props) {
    super(props);
    const { result } = this.props;
    this.state = { membershipRequest: result };
  }

  static contextType = MembershipRequestsContext;

  update = (data, value) => {
    const { membershipRequest } = this.state;
    this.setState({ membershipRequest: { ...membershipRequest, ...{ role: value } } });
  };

  actionSuccessCallback = () => undefined;

  render() {
    const {
      config: { rolesCanAssign },
      community,
    } = this.props;

    const {
      membershipRequest: { member },
      membershipRequest,
    } = this.state;

    const request = buildRequest(membershipRequest, ["accept", "decline"]);
    const { api: membershipRequestsApi } = this.context;
    const roles = rolesCanAssign[member.type];
    const expiration = formattedTime(request.expires_at);

    return (
      <Table.Row className="community-member-item">
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column>
              <Item className="flex align-items-center" key={membershipRequest.id}>
                <Image src={member.avatar} avatar circular className="mr-10" />
                <Item.Content>
                  <Item.Header size="small" as="b">
                    <a href={`/communities/${community.slug}/requests/${request.id}`}>
                      {member.name}
                    </a>
                  </Item.Header>
                  {member.description && (
                    <Item.Meta>
                      <div className="truncate-lines-1">{member.description}</div>
                    </Item.Meta>
                  )}
                </Item.Content>
              </Item>
            </Grid.Column>
          </Grid>
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Status")}>
          <RequestStatus status={request.status} />
        </Table.Cell>
        <Table.Cell
          aria-label={i18next.t("Expires") + " " + expiration}
          data-label={i18next.t("Expires")}
        >
          {expiration}
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Role")}>
          <RoleDropdown
            roles={roles}
            action={membershipRequestsApi.updateRole}
            successCallback={this.update}
            disabled={!membershipRequest.permissions.can_update_role}
            currentValue={membershipRequest.role}
            resource={membershipRequest}
            label={i18next.t("Role") + " " + membershipRequest.role}
          />
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Actions")}>
          <RequestActionController
            request={request}
            actionSuccessCallback={() => {
              window.location.reload();
            }}
          />
        </Table.Cell>
      </Table.Row>
    );
  }
}

MembershipRequestsResultItem.propTypes = {
  result: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
};

MembershipRequestsResultItem.defaultProps = {};
