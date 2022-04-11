/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import { SearchBarWithFiltersWithState } from "../../components/SearchBarWithFilters";

export class MembersSearchLayout extends Component {
  render() {
    const { config, updateQueryState } = this.props;
    const sortOptions = config.sortOptions;
    return (
      <>
        <SearchBarWithFiltersWithState
          searchBarPlaceholder={i18next.t("Search members...")}
          sortOptions={sortOptions}
          updateQueryState={updateQueryState}
        />
        <SearchAppResultsPane layoutOptions={config.layoutOptions} />
      </>
    );
  }
}
