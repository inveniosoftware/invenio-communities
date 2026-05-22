/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import { Table } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";

export const PublicMembersResultsContainer = ({ results }) => {
  return (
    <Table>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell>{i18next.t("Members")}</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Table.Body>{results}</Table.Body>
    </Table>
  );
};

PublicMembersResultsContainer.propTypes = {
  results: PropTypes.array.isRequired,
};
