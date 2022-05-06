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
import { Filters } from "../../Filters";

export class MembersSearchLayout extends Component {
  render() {
    const { config, updateQueryState, roles } = this.props;
    const sortOptions = config.sortOptions;
    const filtersClass = new Filters(roles);
    const customFilters = filtersClass.getMembersFilters();
    return (
      <>
        <SearchBarWithFiltersWithState
          searchBarPlaceholder={i18next.t("Search members...")}
          customFilters={customFilters}
          sortOptions={sortOptions}
          updateQueryState={updateQueryState}
        />
        <SearchAppResultsPane layoutOptions={config.layoutOptions} />
      </>
    );
  }
}
