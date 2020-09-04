import React, { useState } from "react";
import { Card, Item, Button, Icon } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import axios from "axios";
import { createSearchAppInit } from "@js/invenio_search_ui";

// TODO: Use global search config context to get community data
const COMMUNITY_ID = window.location.pathname.split('/')[2];

const ResultsItemTemplate = ({ result, index }) => {
  const community_record = result.metadata._communities.pending.find(
    ({ comid }) => comid === COMMUNITY_ID
  );
  const [status, setStatus] = useState("pending");

  function handleRequest(action) {
    axios
      .post(
        `/api/communities/${community_record.comid}/records/requests/${community_record.id}/${action}`
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

const defaultComponents = {
  "ResultsList.item": ResultsItemTemplate,
  "ResultsGrid.item": ResultsGridItemTemplate,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
