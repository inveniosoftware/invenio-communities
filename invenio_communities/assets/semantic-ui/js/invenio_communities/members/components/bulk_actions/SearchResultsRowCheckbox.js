import { BulkActionsContext } from "./context";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { Checkbox } from "semantic-ui-react";
import _hasIn from "lodash/hasIn";

export class SearchResultsRowCheckbox extends Component {
  static contextType = BulkActionsContext;

  constructor(props) {
    super(props);
    this.state = { isChecked: false };
  }

  componentDidMount() {
    this.subscribeToContext();
    const { bulkActionContext, allSelected } = this.context;
    this.setState({
      isChecked: this.isChecked(bulkActionContext, allSelected),
    });
  }

  isChecked = (bulkActionContext, allSelected) => {
    const { rowId } = this.props;
    if (_hasIn(bulkActionContext, `${rowId}`) || allSelected) {
      return bulkActionContext[rowId];
    }
    return false;
  };

  subscribeToContext = () => {
    const { rowId } = this.props;
    const { allSelected, bulkActionContext } = this.context;
    if (!_hasIn(bulkActionContext, `${rowId}`)) {
      bulkActionContext[rowId] = allSelected;
    }
  };

  handleOnChange = () => {
    const { addToSelected } = this.context;
    const { rowId } = this.props;
    const { isChecked } = this.state;
    this.setState({ isChecked: !isChecked });
    addToSelected(rowId);
  };

  render() {
    const { bulkActionContext, allSelected } = this.context;
    return (
      <>
        <Checkbox
          className="mr-10 mt-10"
          checked={this.isChecked(bulkActionContext, allSelected) || allSelected}
          onChange={this.handleOnChange}
        />
      </>
    );
  }
}

SearchResultsRowCheckbox.propTypes = {
  rowId: PropTypes.string.isRequired,
};
