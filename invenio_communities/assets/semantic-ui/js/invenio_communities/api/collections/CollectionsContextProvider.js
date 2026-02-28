// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CommunityCollectionsApi } from "./api";
import React, { Component } from "react";
import PropTypes from "prop-types";

export const CollectionsContext = React.createContext({ api: undefined });

export class CollectionsContextProvider extends Component {
  constructor(props) {
    super(props);
    const { community } = props;
    this.apiClient = new CommunityCollectionsApi(community);
  }

  render() {
    const { children } = this.props;
    return (
      <CollectionsContext.Provider value={{ api: this.apiClient }}>
        {children}
      </CollectionsContext.Provider>
    );
  }
}

CollectionsContextProvider.propTypes = {
  community: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
};
