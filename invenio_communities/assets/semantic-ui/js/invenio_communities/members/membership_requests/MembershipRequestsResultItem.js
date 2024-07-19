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

import { RoleDropdown } from "../components/dropdowns";
import { formattedTime } from "../utils";

export class MembershipRequestsResultItem extends Component {
  constructor(props) {
    super(props);
    const { result } = this.props;
    this.state = { membershipRequest: result };
  }

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
      membershipRequest: { member, request },
      membershipRequest,
    } = this.state;
    // TODO: Decision flow
    // const { api: membershipRequestsApi } = this.context;
    const rolesCanAssignByType = rolesCanAssign[member.type];
    const membershipRequestExpiration = formattedTime(request.expires_at);
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
          aria-label={i18next.t("Expires") + " " + membershipRequestExpiration}
          data-label={i18next.t("Expires")}
        >
          {membershipRequestExpiration}
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Role")}>
          <RoleDropdown
            roles={rolesCanAssignByType}
            successCallback={this.update}
            // TODO: Decision flow
            // action={membershipRequestsApi.updateRole}
            disabled={!membershipRequest.permissions.can_update_role}
            currentValue={membershipRequest.role}
            resource={membershipRequest}
            label={i18next.t("Role") + " " + membershipRequest.role}
          />
        </Table.Cell>
        <Table.Cell data-label={i18next.t("Actions")}>
          <RequestActionController
            request={membershipRequest}
            // TODO: Decision flow
            actionSuccessCallback={() => console.log("actionSuccessCallback called")}
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
