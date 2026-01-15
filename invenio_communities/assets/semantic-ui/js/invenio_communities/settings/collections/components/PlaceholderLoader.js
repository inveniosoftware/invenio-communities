// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Grid, Placeholder } from "semantic-ui-react";

const PlaceholderLoader = ({ size, isLoading, children }) => {
  const PlaceholderItem = () => (
    <Grid.Column width={3}>
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
    return children;
  }

  return (
    <Grid columns="equal" stackable>
      {numberOfHeader}
    </Grid>
  );
};

PlaceholderLoader.propTypes = {
  size: PropTypes.number,
  isLoading: PropTypes.bool.isRequired,
  children: PropTypes.node.isRequired,
};

PlaceholderLoader.defaultProps = {
  size: 5,
};

export default PlaceholderLoader;
