/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { SearchBarWithFiltersWithState } from "../components/SearchBarWithFilters";
import { InvitationsMembersModalWithState } from "./invitationsModal/InvitationsMembersModal";

export class InvitationsSearchLayout extends Component {
  render() {
    const {
      config,
      roles,
      communityID,
      communityAllowGroupInvites,
    } = this.props;
    const sortOptions = config.sortOptions;
    return (
      <>
        <SearchBarWithFiltersWithState
          sortOptions={sortOptions}
          customCmp={
            <InvitationsMembersModalWithState
              roles={roles}
              communityID={communityID}
              allowGroups={communityAllowGroupInvites}
            />
          }
        />
        <SearchAppResultsPane layoutOptions={config.layoutOptions} />
      </>
    );
  }
}

InvitationsSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  roles: PropTypes.object.isRequired,
  communityID: PropTypes.string.isRequired,
  communityAllowGroupInvites: PropTypes.bool.isRequired,
};
