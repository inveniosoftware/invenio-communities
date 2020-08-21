import React from "react";
import { Input, Item, Card } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { createSearchAppInit } from "@js/invenio_search_ui";

function ResultsGridItemTemplate({ result, index }) {
  return (
    <Card fluid key={index} href={`/communities/${result.metadata.id}`}>
      <Card.Content>
        <Card.Header>{result.metadata.title}</Card.Header>
        <Card.Description>
          <div
            dangerouslySetInnerHTML={{ __html: result.metadata.description }}
          />
        </Card.Description>
      </Card.Content>
    </Card>
  );
}

function ResultsItemTemplate({ result, index }) {
  return (
    <Item key={index} href={`/communities/${result.metadata.id}`}>
      <Item.Content>
        <Item.Header>{result.metadata.title}</Item.Header>
        <Item.Description>
          <div
            dangerouslySetInnerHTML={{ __html: result.metadata.description }}
          />
        </Item.Description>
      </Item.Content>
    </Item>
  );
}

const CommunitiesSearchBarElement = ({
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
  "ResultsList.item": ResultsItemTemplate,
  "ResultsGrid.item": ResultsGridItemTemplate,
  "SearchBar.element": CommunitiesSearchBarElement,
};

// Auto-initialize search app
const initSearchApp = createSearchAppInit(defaultComponents);
