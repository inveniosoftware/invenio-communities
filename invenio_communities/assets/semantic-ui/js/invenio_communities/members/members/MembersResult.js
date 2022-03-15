/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Grid } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { ResultsList, Pagination, ResultsPerPage } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";
import { mockedPublicViewData, mockedMemberViewData } from "../mockedData";
import _upperFirst from "lodash/upperFirst";

export const MembersResults = ({ paginationOptions, currentResultsState }) => {
  // TODO: Remove Mocked data
  // currentResultsState.data = mockedPublicViewData;
  currentResultsState.data = mockedMemberViewData;
  const { total } = currentResultsState.data;
  return (
    total && (
      <Grid>
        <Grid.Row>
          <Grid.Column width={16}>
            <Grid>
              <Grid.Row>
                <Grid.Column>
                  <ResultsList />
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row verticalAlign="middle">
          <Grid.Column width={4}></Grid.Column>
          <Grid.Column width={8} textAlign="center">
            <Pagination
              options={{
                size: "mini",
                showFirst: false,
                showLast: false,
              }}
            />
          </Grid.Column>
          <Grid.Column textAlign="right" width={4}>
            <ResultsPerPage
              values={paginationOptions.resultsPerPage}
              label={(cmp) => (
                <>
                  {" "}
                  {cmp} {i18next.t("results per page")}
                </>
              )}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    )
  );
};
