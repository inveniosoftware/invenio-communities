import { SearchWrapper } from "./search/SearchMain";
import ReactDOM from "react-dom";
import React from "react";
import { Item, Card } from "semantic-ui-react";
import _truncate from "lodash/truncate";

const aggregations = [
  {
    title: "Types",
    agg: {
      field: "type",
      aggName: "type",
    },
  },
  {
    title: "Domains",
    agg: {
      field: "domain",
      aggName: "domain",
    },
  },
];

const sortValues = [
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
];

const resultsPerPageValues = [
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
];

function ResultsGridItemTemplate(record, index) {
  return (
    <Card fluid key={index} href={`/communities/${record.metadata.id}`}>
      <Card.Content>
        <Card.Header>{record.metadata.title}</Card.Header>
        <Card.Description>
          <div
            dangerouslySetInnerHTML={{ __html: record.metadata.description }}
          />
        </Card.Description>
      </Card.Content>
    </Card>
  );
}

function ResultsItemTemplate(record, index) {
  return (
    <Item key={index} href={`/communities/${record.metadata.id}`}>
      <Item.Content>
        <Item.Header>{record.metadata.title}</Item.Header>
        <Item.Description>
          <div
            dangerouslySetInnerHTML={{ __html: record.metadata.description }}
          />
        </Item.Description>
      </Item.Content>
    </Item>
  );
}

const searchApi = {
  axios: {
    baseURL: "",
    url: "/api/communities",
    timeout: 5000,
  },
};

const searchConfig = {
  searchApi,
  aggregations,
  sortValues,
  resultsPerPageValues,
};

ReactDOM.render(
  <SearchWrapper
    ResultsListItem={ResultsItemTemplate}
    ResultsGridItem={ResultsGridItemTemplate}
    searchConfig={searchConfig}
  />,
  document.getElementById("communities-search")
);
