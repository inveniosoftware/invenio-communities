/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { InvitationsContextProvider } from "../../api/invitations/InvitationsContextProvider";
import React, { Component } from "react";
import PropTypes from "prop-types";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { SearchBarWithFiltersWithState } from "../components/SearchBarWithFilters";
import { InvitationsMembersModalWithSearchKit } from "./invitationsModal/InvitationsMembersModal";
import {
  RolePermissionPolicy,
  filterOptionsByPermissions,
} from "../components/bulk_actions/permissions";

export class InvitationsSearchLayout extends Component {
  render() {
    const {
      config,
      roles,
      community,
      permissions,
      communityAllowGroupInvites,
    } = this.props;
    const sortOptions = config.sortOptions;
    return (
      <>
        <SearchBarWithFiltersWithState
          sortOptions={sortOptions}
          customCmp={
            <InvitationsContextProvider community={community}>
              <InvitationsMembersModalWithSearchKit
                roles={filterOptionsByPermissions(
                  roles,
                  RolePermissionPolicy,
                  permissions
                )}
                allowGroups={communityAllowGroupInvites}
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
  roles: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  communityAllowGroupInvites: PropTypes.bool.isRequired,
};
