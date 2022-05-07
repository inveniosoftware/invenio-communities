/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import {
  DropdownFilter,
  DropdownSort,
} from "@js/invenio_communities/members/components/SearchDropdowns";
import { i18next } from "@translations/invenio_communities/i18next";
import _upperFirst from "lodash/upperFirst";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { SearchBar, withState } from "react-searchkit";
import { Button } from "semantic-ui-react";
import FilterLabel from "./FilterLabel";

export class SearchBarWithFilters extends Component {
  render() {
    const {
      sortOptions,
      currentQueryState,
      updateQueryState,
      currentResultsState,
      searchBarPlaceholder,
      customCmp,
      customFilters,
      ...uiProps
    } = this.props;
    const currentFilters = currentQueryState.filters;
    const currentSort = currentQueryState.sortBy;
    const filters = customFilters
      ? customFilters
      : currentResultsState.data.aggregations;

    return (
      <>
        {/* auto column grid used instead of SUI grid for better searchbar width adjustment */}
        <div className="auto-column-grid">
          <div>
            <SearchBar fluid placeholder={searchBarPlaceholder} />
          </div>
          <div>
            {Object.entries(filters).map((filter) => (
              <DropdownFilter
                key={filter[0]}
                filterKey={filter[0]}
                filterLabel={filter[1].label}
                filterValues={filter[1].buckets}
                currentQueryState={currentQueryState}
                updateQueryState={updateQueryState}
                size="large"
                className="fluid-mobile"
                {...uiProps}
              />
            ))}

            {sortOptions && (
              <DropdownSort
                filterKey="sort"
                filterLabel={_upperFirst(currentSort)}
                filterValues={sortOptions}
                currentQueryState={currentQueryState}
                updateQueryState={updateQueryState}
                size="large"
                className="fluid-mobile"
                {...uiProps}
              />
            )}

            {customCmp && customCmp}
          </div>
        </div>

        <div className="rel-mb-1">
          <div>
            {currentFilters.map((filter) => {
              return (
                <FilterLabel
                  key={filter[0]}
                  filter={filter}
                  currentQueryState={currentQueryState}
                  updateQueryState={updateQueryState}
                />
              );
            })}
            {currentFilters.length > 0 && (
              <Button
                primary
                compact
                size="mini"
                onClick={() => {
                  currentQueryState.filters = [];
                  updateQueryState(currentQueryState);
                }}
                className="rel-mr-1 rel-mt-1"
              >
                {i18next.t("Clear all filters")}
              </Button>
            )}
          </div>
        </div>
      </>
    );
  }
}

SearchBarWithFilters.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  sortOptions: PropTypes.array.isRequired,
  searchBarPlaceholder: PropTypes.string,
  customCmp: PropTypes.node,
  customFilters: PropTypes.object,
};

SearchBarWithFilters.defaultProps = {
  searchBarPlaceholder: i18next.t("Search ..."),
  customCmp: null,
  customFilters: undefined,
};

export const SearchBarWithFiltersWithState = withState(SearchBarWithFilters);
