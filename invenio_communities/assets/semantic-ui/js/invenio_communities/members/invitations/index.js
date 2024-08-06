/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { RequestCancelButton } from "@js/invenio_requests/components/Buttons";
import { RequestCancelModalTrigger } from "@js/invenio_requests/components/ModalTriggers";
import {
  SubmitStatus,
  DeleteStatus,
  AcceptStatus,
  DeclineStatus,
  CancelStatus,
  ExpireStatus,
} from "@js/invenio_requests/request";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { DropdownSort } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import { Trans } from "react-i18next";
import { parametrize, overrideStore } from "react-overridable";

import { InvitationsContextProvider as ContextProvider } from "../../api/invitations/InvitationsContextProvider";
import { MemberRequestsSearchBarElement } from "../MemberRequestsSearchBarElement";
import { InvitationsEmptyResults } from "./InvitationsEmptyResults";
import { InvitationResultItem } from "./InvitationResultItem";
import { InvitationsResults } from "./InvitationsResults";
import { InvitationsResultsContainer } from "./InvitationsResultsContainer";
import { InvitationsSearchLayout } from "./InvitationsSearchLayout";

const dataAttr = document.getElementById("community-invitations-search-root").dataset;
const community = JSON.parse(dataAttr.community);
const communitiesAllRoles = JSON.parse(dataAttr.communitiesAllRoles);
const communitiesRolesCanInvite = JSON.parse(dataAttr.communitiesRolesCanInvite);
const permissions = JSON.parse(dataAttr.permissions);

const appName = "InvenioCommunities.InvitationsSearch";

const groupsEnabled = JSON.parse(dataAttr.groupsEnabled);

const InvitationResultItemWithConfig = parametrize(InvitationResultItem, {
  config: { rolesCanInvite: communitiesRolesCanInvite },
  community: community,
});

const InvitationsSearchLayoutWithConfig = parametrize(InvitationsSearchLayout, {
  roles: communitiesAllRoles,
  rolesCanInvite: communitiesRolesCanInvite,
  community: community,
  permissions: permissions,
  groupsEnabled: groupsEnabled,
  appName: appName,
});

const InvitationsSearchBarElement = parametrize(MemberRequestsSearchBarElement, {
  className: "invitation-searchbar",
  placeholder: i18next.t("Search in invitations..."),
});

const InvitationsContextProvider = parametrize(ContextProvider, {
  community: community,
});

const InvitationsResultsContainerWithConfig = parametrize(InvitationsResultsContainer, {
  rolesCanInvite: communitiesRolesCanInvite,
  community: community,
  groupsEnabled: groupsEnabled,
});

const InvitationsEmptyResultsWithCommunity = parametrize(InvitationsEmptyResults, {
  community: community,
  groupsEnabled: groupsEnabled,
  rolesCanInvite: communitiesRolesCanInvite,
});

const InvitationsRequestCancelButton = parametrize(RequestCancelButton, {
  content: i18next.t("Cancel invitation"),
});

const InvitationsRequestActionModalCancelTitle = (props) => {
  return <Trans defaults="{{action}} invitation" values={{ action: "cancel" }} />;
};

const defaultComponents = {
  [`${appName}.EmptyResults.element`]: InvitationsEmptyResultsWithCommunity,
  [`${appName}.SearchApp.layout`]: InvitationsSearchLayoutWithConfig,
  [`${appName}.SearchBar.element`]: InvitationsSearchBarElement,
  [`${appName}.Sort.element`]: DropdownSort,
  [`${appName}.ResultsList.container`]: InvitationsResultsContainerWithConfig,
  [`${appName}.SearchApp.results`]: InvitationsResults,
  [`${appName}.ResultsList.item`]: InvitationResultItemWithConfig,
  "RequestActionModalTrigger.cancel": RequestCancelModalTrigger,
  "RequestActionModal.title.cancel": InvitationsRequestActionModalCancelTitle,
  "RequestActionButton.cancel": InvitationsRequestCancelButton,
  [`RequestStatus.layout.submitted`]: SubmitStatus,
  [`RequestStatus.layout.deleted`]: DeleteStatus,
  [`RequestStatus.layout.accepted`]: AcceptStatus,
  [`RequestStatus.layout.declined`]: DeclineStatus,
  [`RequestStatus.layout.cancelled`]: CancelStatus,
  [`RequestStatus.layout.expired`]: ExpireStatus,
};

const overriddenComponents = overrideStore.getAll();

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true,
  InvitationsContextProvider
);
