/*
 * This file is part of Invenio.
 * Copyright (C) 2017-2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import ReactDOM from "react-dom";
import axios from "axios";
import { Card, Grid, Message, Placeholder } from "semantic-ui-react";
import _truncate from "lodash/truncate";

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
  constructor() {
    super();
    this.imageRef = React.createRef();
  }

  render() {
    return (
      <Card fluid href={`/communities/${this.props.community.id}`}>
        <div className="community-image">
          <img
            ref={this.imageRef}
            className="ui image"
            src={this.props.community.links.logo}
            onError={(error) => {
              if (!this.imageRef.current.src.includes(this.props.defaultLogo))
                this.imageRef.current.src = this.props.defaultLogo;
            }}
          />
        </div>

        <Card.Content>
          <Card.Header>
            {_truncate(this.props.community.metadata.title, { length: 50 })}
          </Card.Header>
          <Card.Description>
            {_truncate(this.props.community.metadata.description, {
              length: 50,
            })}
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
        {this.state.data.hits.length == 0 ? (
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
      defaultLogo="/static/images/placeholder.png"
    />,
    userCommunitiesContainer
  );
}
ReactDOM.render(
  <CommunitiesCardGroup
    fetchDataUrl={`/api/communities?q=&sort=newest&page=1&size=5`}
    emptyMessage="There are no featured communities."
    defaultLogo="/static/images/placeholder.png"
  />,
  featuredCommunitiesContainer
);
export default CommunitiesCardGroup;
