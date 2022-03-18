/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Grid, Label, Dropdown, Button, Icon } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { SearchBar } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import _upperFirst from "lodash/upperFirst";

const triggerButton = (name) => (
  <Button icon fluid>
    {name}
    <Icon name="caret down" />
  </Button>
);

class DropdownFilter extends Component {
  onChangeFilter = (e, data) => {
    const { updateQueryState, currentQueryState } = this.props;
    currentQueryState.filters.push(data.value);
    updateQueryState(currentQueryState);
  };

  render() {
    const { filterKey, filterValues, filterLabel, ...uiProps } = this.props;
    const options = filterValues.map((filterValue) => ({
      key: filterValue.key,
      text: filterValue.label,
      value: [filterKey, filterValue.key],
    }));
    return (
      <Dropdown
        {...uiProps}
        icon={null}
        trigger={triggerButton(filterLabel)}
        options={options}
        onChange={this.onChangeFilter}
        selectOnBlur={false}
      />
    );
  }
}

DropdownFilter.propTypes = {
  updateQueryState: PropTypes.object.isRequired,
  currentQueryState: PropTypes.func.isRequired,
  filterKey: PropTypes.string.isRequired,
  filterValues: PropTypes.array.isRequired,
  filterLabel: PropTypes.string.isRequired,
};

class DropdownSort extends Component {
  onChangeSort = (e, data) => {
    const { updateQueryState, currentQueryState } = this.props;
    currentQueryState.sortBy = data.value;
    updateQueryState(currentQueryState);
  };

  render() {
    const { filterKey, filterValues, filterLabel, ...uiProps } = this.props;
    const options = filterValues.map((filterValue) => ({
      key: filterValue.sortBy,
      text: filterValue.text,
      value: filterValue.sortBy,
    }));
    return (
      <Dropdown
        {...uiProps}
        icon={null}
        trigger={triggerButton(filterLabel)}
        options={options}
        onChange={this.onChangeSort}
        selectOnBlur={false}
      />
    );
  }
}

DropdownSort.propTypes = {
  updateQueryState: PropTypes.object.isRequired,
  currentQueryState: PropTypes.func.isRequired,
  filterKey: PropTypes.string.isRequired,
  filterValues: PropTypes.array.isRequired,
  filterLabel: PropTypes.string.isRequired,
};

class FilterLabel extends Component {
  render() {
    const { filter, currentQueryState, updateQueryState } = this.props;
    const currentFilters = currentQueryState.filters;
    const filterType = _upperFirst(filter[0]);
    const filterValue = _upperFirst(filter[1]);
    return (
      <Label className="ml-15 mt-15">
        {`${filterType}: ${filterValue}`}
        <Icon
          onClick={() => {
            const start = currentFilters.indexOf(filter);
            currentFilters.splice(start, 1);
            updateQueryState(currentQueryState);
          }}
          name="delete"
        />
      </Label>
    );
  }
}

FilterLabel.propTypes = {
  updateQueryState: PropTypes.object.isRequired,
  currentQueryState: PropTypes.func.isRequired,
  filter: PropTypes.array.isRequired,
};

class SortLabel extends Component {
  render() {
    const { sort, currentQueryState, updateQueryState } = this.props;
    const sortValue = _upperFirst(sort);
    return (
      <Label className="ml-15 mt-15">
        {`${i18next.t("Sort")}: ${sortValue}`}
        <Icon
          onClick={() => {
            currentQueryState.sortBy = undefined;
            updateQueryState(currentQueryState);
          }}
          name="delete"
        />
      </Label>
    );
  }
}

SortLabel.propTypes = {
  updateQueryState: PropTypes.object.isRequired,
  currentQueryState: PropTypes.func.isRequired,
  sort: PropTypes.string.isRequired,
};

export class SearchBarWithFilters extends Component {
  render() {
    const {
      filters,
      sortOptions,
      currentQueryState,
      updateQueryState,
      searchBarPlaceholder,
      customCmp,
      ...uiProps
    } = this.props;
    const currentFilters = currentQueryState.filters;
    const currentSort = currentQueryState.sortBy;
    return (
      <Grid.Row>
        <Grid.Column
          className="searchbar-with-filters"
          computer={16}
          tablet={16}
        >
          <SearchBar
            uiProps={{ className: "searchbar-with-filters" }}
            placeholder={searchBarPlaceholder}
          />
          <div>
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
                filterLabel={i18next.t("Sort")}
                filterValues={sortOptions}
                currentQueryState={currentQueryState}
                updateQueryState={updateQueryState}
                {...uiProps}
              />
            )}
          </div>
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
        {currentSort && (
          <SortLabel
            sort={currentSort}
            currentQueryState={currentQueryState}
            updateQueryState={updateQueryState}
          />
        )}
        {currentFilters.length > 0 && (
          <Label
            as="a"
            onClick={() => {
              currentQueryState.filters = [];
              currentQueryState.sortBy = undefined;
              updateQueryState(currentQueryState);
            }}
            color="red"
            className="ml-15 mt-15"
          >
            {i18next.t("Clear all filters")}
          </Label>
        )}
      </Grid.Row>
    );
  }
}

SearchBarWithFilters.propTypes = {
  updateQueryState: PropTypes.object.isRequired,
  currentQueryState: PropTypes.func.isRequired,
  sortOptions: PropTypes.array.isRequired,
  filters: PropTypes.object.isRequired,
  searchBarPlaceholder: PropTypes.string,
  customCmp: PropTypes.node,
};

SearchBarWithFilters.defaultProps = {
  searchBarPlaceholder: i18next.t("Search ..."),
  customCmp: null,
};
