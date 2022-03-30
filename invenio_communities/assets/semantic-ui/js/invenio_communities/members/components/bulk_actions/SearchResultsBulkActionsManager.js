import { BulkActionsContext } from "./context";
import React, { Component } from "react";
import Overridable from "react-overridable";
import _hasIn from "lodash/hasIn";

class SearchResultsBulkActionsManager extends Component {
  constructor(props) {
    super(props);

    this.selected = {};
    this.state = { allSelected: false, selectedCount: 0 };
  }

  addToSelected = (rowId) => {
    const { selectedCount } = this.state;

    if (_hasIn(this.selected, `${rowId}`)) {
      this.selected[rowId] = !this.selected[rowId];
    } else {
      this.selected[rowId] = true;
    }

    if (!this.selected[rowId]) {
      this.setAllSelected(false);
      this.setSelectedCount(selectedCount-1);
    } else {
      const updatedCount = selectedCount+1;
      this.setSelectedCount(updatedCount);
      if(Object.keys(this.selected).length === updatedCount){
        this.setAllSelected(true);
      }
    }
  };

  setSelectedCount = (count) =>{
    this.setState({selectedCount: count})
  }

  setAllSelected = (val, global = false) => {
    this.setState({ allSelected: val });
    if (global) {
      for (const [key, value] of Object.entries(this.selected)) {
        this.selected[key] = val;
      }
      if(val){
        this.setSelectedCount(Object.keys(this.selected).length)
      }
      else{
        this.setSelectedCount(0);
      }
    }
  };

  render() {
    const { children } = this.props;
    const { allSelected, selectedCount } = this.state;
    return (
      <Overridable id="SearchResultsBulkActionsManager.layout">
        <BulkActionsContext.Provider
          value={{
            bulkActionContext: this.selected,
            addToSelected: this.addToSelected,
            setAllSelected: this.setAllSelected,
            allSelected: allSelected,
            selectedCount: selectedCount,
          }}
        >
          {children}
        </BulkActionsContext.Provider>
      </Overridable>
    );
  }
}

SearchResultsBulkActionsManager.contextType = BulkActionsContext;

SearchResultsBulkActionsManager.propTypes = {};

export default Overridable.component(
  "SearchResultsBulkActionsManager",
  SearchResultsBulkActionsManager
);
