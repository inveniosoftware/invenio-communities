import React, { Component } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";
import { Checkbox, Dropdown } from "semantic-ui-react";
import { BulkActionsContext } from "./context";
import Overridable from "react-overridable";
import _pickBy from "lodash/pickBy";

export class SearchResultsBulkActions extends Component {
  static contextType = BulkActionsContext;

  constructor(props) {
    super(props);
    const { allSelected } = this.props;
    this.state = { allSelectedChecked: allSelected, action: undefined };
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

  handleActionOnChange = (e, { value, ...props }) => {
    if (!value) return;

    const { optionSelectionCallback } = this.props;
    this.setState({ action: value });

    const { selectedCount, bulkActionContext } = this.context;
    const selected = _pickBy(
      bulkActionContext,
      ({ selected }) => selected === true
    );
    optionSelectionCallback(value, selected, selectedCount);
    this.setState({ action: undefined });
  };

  render() {
    const { bulkDropdownOptions } = this.props;
    const { allSelectedChecked, action } = this.state;
    const { allSelected, selectedCount } = this.context;

    const dropdownOptions = bulkDropdownOptions.map(({ key, value, text }) => ({
      key: key,
      value: value,
      text: text,
    }));

    return (
      <Overridable id="SearchResultsBulkActionsManager.layout">
        <div className="flex">
          <Checkbox
            className="align-self-center mr-10"
            onChange={this.handleOnChange}
            checked={allSelectedChecked && allSelected}
          />
          <Dropdown
            className="align-self-center"
            text={`${selectedCount} ${i18next.t("members selected")}`}
            options={dropdownOptions}
            item
            selection
            value={action}
            defaultValue={undefined}
            onChange={this.handleActionOnChange}
          />
        </div>
      </Overridable>
    );
  }
}

SearchResultsBulkActions.propTypes = {
  bulkDropdownOptions: PropTypes.array.isRequired,
  allSelected: PropTypes.bool,
  optionSelectionCallback: PropTypes.func.isRequired,
};

SearchResultsBulkActions.defaultProps = {
  allSelected: false,
};

export default Overridable.component(
  "SearchResultsBulkActions",
  SearchResultsBulkActions
);
