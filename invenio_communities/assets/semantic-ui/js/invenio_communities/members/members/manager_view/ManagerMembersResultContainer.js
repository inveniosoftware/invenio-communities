/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React, { Component } from "react";
import { ManagerMemberBulkActions } from "./ManagerMemberBulkActions";
import { Table } from "semantic-ui-react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { ManagerMembersResultItem } from "./ManagerMembersResultItem";

export class ManagerMembersResultsContainer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      results: props.results,
    };
  }

  updateResults = (members, actionParameter) => {
    const { results } = this.state;
    const { config } = this.props;
    const newResults = results.map((result) => {
      Object.keys(members).forEach((member) => {
        if (result.props.result.id === member) {
          result.props.result.role = actionParameter;
        }
      });
      result = (
        <ManagerMembersResultItem
          result={result.props.result}
          config={config}
        />
      );
      return result;
    });
    this.setState({ results: newResults });
  };

  render() {
    const { community, config } = this.props;
    const { results } = this.state;
    return (
      <Table>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell width={6}>
              <ManagerMemberBulkActions
                community={community}
                roles={config.roles}
                visibilities={config.visibility}
                permissions={config.permissions}
                updateResultsCallback={this.updateResults}
              />
            </Table.HeaderCell>
            <Table.HeaderCell width={2}>
              {i18next.t("Member since")}
            </Table.HeaderCell>
            <Table.HeaderCell width={2}>
              {i18next.t("Visibility")}
            </Table.HeaderCell>
            <Table.HeaderCell width={4}>{i18next.t("Role")}</Table.HeaderCell>
            <Table.HeaderCell width={2} />
          </Table.Row>
        </Table.Header>
        <Table.Body>{results}</Table.Body>
      </Table>
    );
  }
}

ManagerMembersResultsContainer.propTypes = {
  results: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
};
