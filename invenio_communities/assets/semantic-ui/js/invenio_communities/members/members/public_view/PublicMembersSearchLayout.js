/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Grid } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { SearchBar } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";
import _upperFirst from "lodash/upperFirst";

const PublicViewSearchBar = () => {
  return (
    <Grid>
      <Grid.Row columns={2}>
        <Grid.Column width={16}>
          <SearchBar placeholder={i18next.t("Search members...")} />
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};

export class PublicMembersSearchLayout extends Component {
  render() {
    const { config, updateQueryState } = this.props;
    const sortOptions = config.sortOptions;
    return (
      <>
        <PublicViewSearchBar />
        <SearchAppResultsPane layoutOptions={config.layoutOptions} />
      </>
    );
  }
}
