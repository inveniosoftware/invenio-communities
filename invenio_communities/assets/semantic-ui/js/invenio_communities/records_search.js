import React from "react";
import { Input } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { defaultComponents as searchDefaultComponents, createSearchAppInit } from "@js/invenio_search_ui";


// TODO: Remove after https://github.com/inveniosoftware/react-searchkit/issues/117
// is addressed
const CommunitiesRecordsSearchBarElement = ({
  placeholder: passedPlaceholder,
  queryString,
  onInputChange,
  executeSearch,
}) => {
  const placeholder = passedPlaceholder || "Search";
  const onBtnSearchClick = () => {
    executeSearch();
  };
  const onKeyPress = (event) => {
    if (event.key === "Enter") {
      executeSearch();
    }
  };
  return (
    <Input
      action={{
        icon: "search",
        onClick: onBtnSearchClick,
        className: "search",
      }}
      placeholder={placeholder}
      onChange={(event, { value }) => {
        onInputChange(value);
      }}
      value={queryString}
      onKeyPress={onKeyPress}
    />
  );
};

const defaultComponents = {
  // Use default record result list/grid item components
  ...searchDefaultComponents,
  "SearchBar.element": CommunitiesRecordsSearchBarElement,
};

// Auto-initialize search app
const initSearchApp = createSearchAppInit(defaultComponents);
