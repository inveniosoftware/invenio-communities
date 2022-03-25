/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Table } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { i18next } from "@translations/invenio_communities/i18next";
import _upperFirst from "lodash/upperFirst";

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
