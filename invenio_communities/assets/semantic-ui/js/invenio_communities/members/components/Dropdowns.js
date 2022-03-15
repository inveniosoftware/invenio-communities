/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Dropdown, Button, Icon, Menu } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import PropTypes from "prop-types";
import _upperFirst from "lodash/upperFirst";

const triggerButton = (name) => (
  <Button icon fluid>
    {name}
    <Icon name="caret down" />
  </Button>
);

export class DropdownSort extends Component {
  onChangeSort = (e, data) => {
    const { updateQueryState, currentQueryState } = this.props;
    currentQueryState.sortBy = data.value;
    updateQueryState(currentQueryState);
  };

  render() {
    const {
      filterKey,
      filterValues,
      filterLabel,
      updateQueryState,
      currentQueryState,
      ...uiProps
    } = this.props;
    const options = filterValues.map((filterValue) => {
      const disabled = currentQueryState.sortBy === filterValue.sortBy;
      return {
        key: filterValue.sortBy,
        text: filterValue.text,
        value: filterValue.sortBy,
        disabled: disabled,
      };
    });

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
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  filterKey: PropTypes.string.isRequired,
  filterValues: PropTypes.array.isRequired,
  filterLabel: PropTypes.string.isRequired,
};

DropdownSort.defaultProps = {
  filterLabel: "",
};

export class DropdownFilter extends Component {
  onChangeFilter = (e, data) => {
    const { updateQueryState, currentQueryState } = this.props;
    currentQueryState.filters.push(JSON.parse(data.value));
    updateQueryState(currentQueryState);
  };

  render() {
    const {
      filterKey,
      filterValues,
      filterLabel,
      currentQueryState,
      updateQueryState,
      loading,
      ...uiProps
    } = this.props;
    const options = filterValues.map((filterValue) => {
      const value = [filterKey, filterValue.key];
      const disabled = currentQueryState.filters.some(
        (filter) => JSON.stringify(value) === JSON.stringify(filter)
      );
      return {
        key: filterValue.key,
        text: filterValue.label,
        value: JSON.stringify(value),
        disabled: disabled,
      };
    });

    return (
      <Dropdown
        {...uiProps}
        icon={null}
        trigger={triggerButton(filterLabel)}
        options={options}
        onChange={this.onChangeFilter}
        selectOnBlur={false}
        value={null}
      />
    );
  }
}

DropdownFilter.propTypes = {
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  filterKey: PropTypes.string.isRequired,
  filterValues: PropTypes.array.isRequired,
  filterLabel: PropTypes.string.isRequired,
};

DropdownFilter.defaultProps = {
  filterLabel: "",
};

export class MemberDropdown extends Component {
  constructor(props) {
    const { initialValue } = props;
    super(props);
    this.state = {
      value: initialValue,
    };
  }
  render() {
    const { options, updateMember } = this.props;
    const { value } = this.state;
    return (
      <Menu compact>
        <Dropdown
          text={_upperFirst(value)}
          options={options}
          item
          fluid
          openOnFocus={false}
          selectOnBlur={false}
          onChange={(e, data) => {
            updateMember(data.value);
            this.setState({
              value: data.value,
            });
          }}
        />
      </Menu>
    );
  }
}

MemberDropdown.propTypes = {
  options: PropTypes.array.isRequired,
  updateMember: PropTypes.func.isRequired,
  initialValue: PropTypes.string,
};

MemberDropdown.defaultProps = {
  initialValue: "",
};
