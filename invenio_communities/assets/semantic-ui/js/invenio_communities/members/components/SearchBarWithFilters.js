/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Grid, Label } from "semantic-ui-react";
import { SearchBar, withState } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import _upperFirst from "lodash/upperFirst";
import { DropdownFilter, DropdownSort } from "./Dropdowns";
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
      ...uiProps
    } = this.props;
    const currentFilters = currentQueryState.filters;
    const currentSort = currentQueryState.sortBy;
    const filters = currentResultsState.data.aggregations; // TODO: filters come from the backend
    return (
      <Grid>
        <Grid.Row>
          <Grid.Column className="flex-container" width={16}>
            <SearchBar
              uiProps={{ className: "contents-container" }}
              placeholder={searchBarPlaceholder}
            />
            <>
              {Object.entries(filters).map((filter) => (
                <DropdownFilter
                  className="ml-20"
                  filterKey={filter[0]}
                  filterLabel={filter[1].label}
                  filterValues={filter[1].buckets}
                  currentQueryState={currentQueryState}
                  updateQueryState={updateQueryState}
                  {...uiProps}
                />
              ))}
              {sortOptions && (
                <DropdownSort
                  className="ml-20"
                  filterKey="sort"
                  filterLabel={_upperFirst(currentSort)}
                  filterValues={sortOptions}
                  currentQueryState={currentQueryState}
                  updateQueryState={updateQueryState}
                  {...uiProps}
                />
              )}
            </>
            {customCmp && customCmp}
          </Grid.Column>

          {currentFilters.map((filter) => {
            return (
              <FilterLabel
                filter={filter}
                currentQueryState={currentQueryState}
                updateQueryState={updateQueryState}
              />
            );
          })}

          {currentFilters.length > 0 && (
            <Label
              as="a"
              onClick={() => {
                currentQueryState.filters = [];
                updateQueryState(currentQueryState);
              }}
              color="blue"
              className="ml-15 mt-15"
            >
              {i18next.t("Clear all filters")}
            </Label>
          )}
        </Grid.Row>
      </Grid>
    );
  }
}

SearchBarWithFilters.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  sortOptions: PropTypes.array.isRequired,
  searchBarPlaceholder: PropTypes.string,
  customCmp: PropTypes.node,
};

SearchBarWithFilters.defaultProps = {
  searchBarPlaceholder: i18next.t("Search ..."),
  customCmp: null,
};

export const SearchBarWithFiltersWithState = withState(SearchBarWithFilters);
