// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 Northwestern University.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CommunityMembershipRequestsApi } from "./api";
import React, { Component } from "react";
import PropTypes from "prop-types";

export const MembershipRequestsContext = React.createContext({ api: undefined });

export class MembershipRequestsContextProvider extends Component {
  constructor(props) {
    super(props);
    const { community } = props;
    this.apiClient = new CommunityMembershipRequestsApi(community);
  }
  render() {
    const { children } = this.props;
    return (
      <MembershipRequestsContext.Provider value={{ api: this.apiClient }}>
        {children}
      </MembershipRequestsContext.Provider>
    );
  }
}

MembershipRequestsContextProvider.propTypes = {
  community: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
};
