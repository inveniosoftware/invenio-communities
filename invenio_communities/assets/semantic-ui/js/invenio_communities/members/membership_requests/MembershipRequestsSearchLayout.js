/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { RequestStatusFilter } from "@js/invenio_requests/search";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { SearchFilters } from "@js/invenio_search_ui/components/SearchFilters";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { SearchBar, Sort } from "react-searchkit";

import { Filters } from "../Filters";
import { FilterLabels } from "../components/FilterLabels";

export class MembershipRequestsSearchLayout extends Component {
  render() {
    const { config, roles, appName } = this.props;

    const filtersClass = new Filters(roles);
    const customFilters = filtersClass.getMembershipRequestFilters();

    return (
      <>
        {/* auto column grid used instead of SUI grid for better searchbar width adjustment */}
        <div className="auto-column-grid">
          <div className="flex column-mobile">
            <div className="mobile only rel-mb-1 flex align-items-center justify-space-between">
              <RequestStatusFilter keepFiltersOnUpdate />
            </div>
            <div className="tablet computer only only rel-mr-2">
              <RequestStatusFilter keepFiltersOnUpdate />
            </div>
            <SearchBar fluid />
          </div>
          <div className="flex align-items-center column-mobile">
            <div className="tablet only mr-5" />
            <div className="full-width flex align-items-center justify-end column-mobile">
              <SearchFilters customFilters={customFilters} />
              <Sort values={config.sortOptions} />
            </div>
          </div>
        </div>
        <div className="rel-mb-1">
          <FilterLabels ignoreFilters={["is_open"]} />
        </div>
        <SearchAppResultsPane layoutOptions={config.layoutOptions} appName={appName} />
      </>
    );
  }
}

MembershipRequestsSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  roles: PropTypes.array.isRequired,
  appName: PropTypes.string,
};

MembershipRequestsSearchLayout.defaultProps = {
  appName: "",
};
