/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { Label, Icon } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import PropTypes from "prop-types";
import _upperFirst from "lodash/upperFirst";

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
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  filter: PropTypes.array.isRequired,
};

export default FilterLabel;
