/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { InvitationsContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { SearchBarWithFiltersWithState } from "../components/SearchBarWithFilters";
import { Filters } from "../Filters";
import { InvitationsMembersModalWithSearchKit } from "./invitationsModal/InvitationsMembersModal";

export class InvitationsSearchLayout extends Component {
  render() {
    const {
      config,
      roles,
      rolesCanInvite,
      community,
      communityGroupsEnabled,
    } = this.props;

    const sortOptions = config.sortOptions;
    const filtersClass = new Filters(roles);
    const customFilters = filtersClass.getInvitationFilters();
    return (
      <>
        <SearchBarWithFiltersWithState
          sortOptions={sortOptions}
          customFilters={customFilters}
          customCmp={
            <InvitationsContextProvider community={community}>
              <InvitationsMembersModalWithSearchKit
                rolesCanInvite={rolesCanInvite}
                groupsEnabled={communityGroupsEnabled}
                community={community}
              />
            </InvitationsContextProvider>
          }
        />
        <SearchAppResultsPane layoutOptions={config.layoutOptions} />
      </>
    );
  }
}

InvitationsSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  roles: PropTypes.array.isRequired,
  rolesCanInvite: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  communityGroupsEnabled: PropTypes.bool.isRequired,
};
