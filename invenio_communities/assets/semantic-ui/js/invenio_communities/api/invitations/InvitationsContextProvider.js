/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { CommunityInvitationsApi } from "./api";
import { Component, createContext } from "react";
import PropTypes from "prop-types";

export const InvitationsContext = createContext({ api: undefined });

export class InvitationsContextProvider extends Component {
  constructor(props) {
    super(props);
    const { community } = props;
    this.apiClient = new CommunityInvitationsApi(community);
  }
  render() {
    const { children } = this.props;
    return (
      <InvitationsContext.Provider value={{ api: this.apiClient }}>
        {children}
      </InvitationsContext.Provider>
    );
  }
}

InvitationsContextProvider.propTypes = {
  community: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
};
