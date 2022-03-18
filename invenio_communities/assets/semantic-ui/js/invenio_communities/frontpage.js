/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import { Card, Grid, Message, Placeholder } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { Image } from "react-invenio-forms";

const PlaceholderLoader = ({ size = 5, isLoading, ...props }) => {
  const PlaceholderItem = () => (
    <Grid.Column width={3}>
      <Placeholder>
        <Placeholder.Image square />
      </Placeholder>
      <Placeholder>
        <Placeholder.Paragraph>
          <Placeholder.Line length="medium" />
          <Placeholder.Line length="short" />
        </Placeholder.Paragraph>
      </Placeholder>
    </Grid.Column>
  );
  let numberOfHeader = [];
  for (let i = 0; i < size; i++) {
    numberOfHeader.push(<PlaceholderItem key={i} />);
  }

  if (!isLoading) {
    return props.children;
  }
  return (
    <Grid columns="equal" stackable>
      {numberOfHeader}
    </Grid>
  );
};

const EmptyMessage = ({ message }) => {
  return <Message icon="info" header={message} />;
};

class CommunityCard extends Component {

  render() {
    return (
      <Card fluid href={`/communities/${this.props.community.id}`}>
        <Image
          src={this.props.community.links.logo}
          fallbackSrc={this.props.defaultLogo}
        />
        <Card.Content>
          <Card.Header>
            {_truncate(this.props.community.metadata.title, { length: 50 })}
          </Card.Header>
          <Card.Description>
            <div
              className="truncate-lines-2"
              dangerouslySetInnerHTML={{
                __html: this.props.community.metadata.description,
              }}
            />
          </Card.Description>
        </Card.Content>
      </Card>
    );
  }
}

class CommunitiesCardGroup extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isLoading: false,
      data: { hits: [] },
      error: {},
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  fetchData = async () => {
    this.setState({ isLoading: true });
    try {
      const response = await axios(this.props.fetchDataUrl, {
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        withCredentials: true,
      });
      this.setState({ data: response.data.hits, isLoading: false });
    } catch (error) {
      // TODO: handle error response
    }
  };

  renderCards() {
    const { data } = this.state;
    return data.hits.map((community) => {
      return (
        <CommunityCard
          key={community.id}
          community={community}
          defaultLogo={this.props.defaultLogo}
        />
      );
    });
  }

  render() {
    const { isLoading } = this.state;
    return (
      <PlaceholderLoader isLoading={isLoading}>
        {this.state.data.hits.length === 0 ? (
          <EmptyMessage message={this.props.emptyMessage} />
        ) : (
          <Card.Group itemsPerRow={5} className="community-frontpage-cards">
            {this.renderCards()}
          </Card.Group>
        )}
      </PlaceholderLoader>
    );
  }
}

const userCommunitiesContainer = document.getElementById("user-communities");
const featuredCommunitiesContainer = document.getElementById(
  "featured-communities"
);

if (userCommunitiesContainer) {
  ReactDOM.render(
    <CommunitiesCardGroup
      fetchDataUrl={`/api/user/communities?q=&sort=newest&page=1&size=5`}
      emptyMessage="You are not a member of any community."
      defaultLogo="/static/images/square-placeholder.png"
    />,
    userCommunitiesContainer
  );
}
ReactDOM.render(
  <CommunitiesCardGroup
    fetchDataUrl={`/api/communities?q=&sort=newest&page=1&size=5`}
    emptyMessage="There are no featured communities."
    defaultLogo="/static/images/square-placeholder.png"
  />,
  featuredCommunitiesContainer
);
export default CommunitiesCardGroup;
