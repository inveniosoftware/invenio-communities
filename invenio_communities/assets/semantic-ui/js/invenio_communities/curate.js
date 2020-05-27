import ReactDOM from "react-dom";
import React, { useState } from "react";
import { Card, Item, Button, Icon } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import axios from "axios";
import { SearchApp } from "../invenio_search_ui/SearchApp";
import { overrideStore } from "react-overridable";

const ResultsItemTemplate = ({ result, index }) => {
  const request = result.metadata._communities.pending.find(
    ({ id }) => id === COMMUNITY_ID
  );
  const [status, setStatus] = useState("pending");

  function handleRequest(action) {
    axios
      .post(
        `/api/communities/${request.comid}/requests/inclusion/${request.request_id}/${action}`
      )
      .then((response) => {
        setStatus(action);
        console.log(response);
      });
  }

  return (
    <Item key={index}>
      <Item.Content>
        <Item.Header href={`/records/${result.id}`}>
          {result.metadata.titles[0].title}
        </Item.Header>
        <Item.Description>
          <Button
            size="tiny"
            positive
            disabled={status !== "pending"}
            onClick={() => handleRequest("accept")}
          >
            <Icon name="check" /> Accept
          </Button>
          <Button
            size="tiny"
            negative
            disabled={status !== "pending"}
            onClick={() => handleRequest("reject")}
          >
            <Icon name="delete" inverted /> Reject
          </Button>
          <Button
            size="tiny"
            disabled
            // onClick={() => handleRequest("comment")}
          >
            <Icon name="comment" /> Comment
          </Button>
        </Item.Description>
        <Item.Extra>
          {status === "pending" ? null : (
            <span>Record was successfully {status}ed</span>
          )}
        </Item.Extra>
      </Item.Content>
    </Item>
  );
};

function ResultsGridItemTemplate({ result, index }) {
  return (
    <Card fluid key={index} href={`/records/${result.id}`}>
      <Card.Content>
        <Card.Header>{result.metadata.titles[0].title}</Card.Header>
        <Card.Description>
          {_truncate(result.metadata.descriptions[0].description, {
            length: 200,
          })}
        </Card.Description>
      </Card.Content>
    </Card>
  );
}

overrideStore.add("ResultsList.item", ResultsItemTemplate);
overrideStore.add("ResultsGrid.item", ResultsGridItemTemplate);

const domContainer = document.getElementById("community-id");
const COMMUNITY_ID = domContainer.dataset.communityId;
const searchConfig = {
  api: `/api/records?q=_communities.pending.id:"${COMMUNITY_ID}"`,
  mimetype: "application/json",
  aggs: [
    {
      title: "Access Right",
      field: "access_right",
      aggName: "access_right",
    },
    {
      title: "Resource types",
      field: "resource_type",
      aggName: "resource_type",
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
  <SearchApp config={searchConfig} appName={"communities-records-curate"} />,
  document.getElementById("communities-records-curate")
);
