import ReactDOM from "react-dom";
import React from "react";
import { Item, Card } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { SearchApp } from "../invenio_search_ui/SearchApp";
import { overrideStore } from "react-overridable";

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

overrideStore.add("ResultsList.item", ResultsItemTemplate);
overrideStore.add("ResultsGrid.item", ResultsGridItemTemplate);

const searchConfig = {
  api: "/api/communities",
  mimetype: "application/json",
  aggs: [
    {
      title: "Types",
      field: "type",
      aggName: "type",
    },
    {
      title: "Domains",
      field: "domain",
      aggName: "domain",
    },
  ],
  sort_options: [
    {
      text: "Best match",
      sortBy: "bestmatch",
      sortOrder: "desc",
      defaultOnEmptyString: true,
    },
    {
      text: "Newest",
      sortBy: "mostrecent",
      sortOrder: "asc",
      default: true,
    },
    {
      text: "Oldest",
      sortBy: "mostrecent",
      sortOrder: "desc",
    },
  ],
  resultsPerPageValues: [
    {
      text: "10",
      value: 10,
    },
    {
      text: "20",
      value: 20,
    },
    {
      text: "50",
      value: 50,
    },
  ],
};

ReactDOM.render(
  <SearchApp config={searchConfig} appName={"communities-search"} />,
  document.getElementById("communities-search")
);
