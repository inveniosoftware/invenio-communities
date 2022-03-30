/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import SearchResultsBulkActions from "../../components/bulk_actions/SearchResultsBulkActions";
import React from "react";
import { Table } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

export const ManagerMembersResultsContainer = ({ results, totalResults }) => {
  const options = [
    { key: 1, value: "change_role", text: i18next.t("Change role") },
    { key: 2, value: "change_visibility", text: i18next.t("Change role") },
    { key: 3, value: "remove_from_community", text: i18next.t("Remove from community") },
  ];
  console.log(totalResults);
  return (
    <Table>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell width={7}>
            <div className="flex">
              <SearchResultsBulkActions
                bulkDropdownOptions={options}
                bulkId="members-search"
              />
            </div>
          </Table.HeaderCell>
          <Table.HeaderCell width={2}>
            {i18next.t("Member since")}
          </Table.HeaderCell>
          <Table.HeaderCell width={2}>
            {i18next.t("Visibility")}
          </Table.HeaderCell>
          <Table.HeaderCell width={2}>{i18next.t("Role")}</Table.HeaderCell>
          <Table.HeaderCell width={2} />
        </Table.Row>
      </Table.Header>
      <Table.Body>{results}</Table.Body>
    </Table>
  );
};
