import React, { Component } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { Checkbox, Dropdown } from "semantic-ui-react";
import { BulkActionsContext } from "./context";
import Overridable from "react-overridable";

export class SearchResultsBulkActions extends Component {
  static contextType = BulkActionsContext;

  constructor(props) {
    super(props);
    const { allSelected } = this.props;
    this.state = { allSelectedChecked: allSelected };
  }

  componentDidMount() {
    const { allSelected } = this.context;
    this.setState({ allSelectedChecked: allSelected });
  }

  handleOnChange = () => {
    const { setAllSelected, allSelected } = this.context;
    this.setState({ allSelectedChecked: !allSelected });
    setAllSelected(!allSelected, true);
  };

  render() {
    const { bulkDropdownOptions } = this.props;
    const { allSelectedChecked } = this.state;
    const { allSelected, selectedCount } = this.context;

    return (
      <Overridable id="SearchResultsBulkActionsManager.layout">
        <>
          <Checkbox
            className="align-self-center mr-10"
            onChange={this.handleOnChange}
            checked={allSelectedChecked && allSelected}
          />
          <Dropdown
            className="align-self-center"
            text={`${selectedCount} ${i18next.t("members selected")}`}
            options={bulkDropdownOptions}
            item
            selection
          />
        </>
      </Overridable>
    );
  }
}

SearchResultsBulkActions.propTypes = {
  bulkDropdownOptions: PropTypes.array.isRequired,
  allSelected: PropTypes.bool,
};

SearchResultsBulkActions.defaultProps = {
  allSelected: false,
};

export default Overridable.component(
  "SearchResultsBulkActions",
  SearchResultsBulkActions
);
