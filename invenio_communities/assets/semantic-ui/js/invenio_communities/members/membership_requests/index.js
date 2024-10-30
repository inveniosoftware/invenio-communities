/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { parametrize, overrideStore } from "react-overridable";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { DropdownSort } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import {
  RequestAcceptButton,
  RequestDeclineButton,
} from "@js/invenio_requests/components/Buttons";
import {
  RequestAcceptModalTrigger,
  RequestDeclineModalTrigger,
} from "@js/invenio_requests/components/ModalTriggers";
import {
  SubmitStatus,
  DeleteStatus,
  AcceptStatus,
  DeclineStatus,
  CancelStatus,
  ExpireStatus,
} from "@js/invenio_requests/request";

import { MembershipRequestsContextProvider as ContextProvider } from "../../api/membershipRequests/MembershipRequestsContextProvider";
import { MemberRequestsResults } from "../MemberRequestsResults";
import { MemberRequestsSearchBarElement } from "../MemberRequestsSearchBarElement";
import { MembershipRequestsEmptyResults } from "./MembershipRequestsEmptyResults";
import { MembershipRequestsResultsContainer } from "./MembershipRequestsResultsContainer";
import { MembershipRequestsResultItem as ResultItem } from "./MembershipRequestsResultItem";
import { MembershipRequestsSearchLayout as SearchLayout } from "./MembershipRequestsSearchLayout";

const dataAttr = document.getElementById(
  "community-membership-requests-search-root"
).dataset;
const community = JSON.parse(dataAttr.community);
const communitiesAllRoles = JSON.parse(dataAttr.communitiesAllRoles);
const communitiesRolesCanAssign = JSON.parse(dataAttr.communitiesRolesCanAssign);

const appName = "InvenioCommunities.MembershipRequestsSearch";

const MembershipRequestsContextProvider = parametrize(ContextProvider, {
  community: community,
});

const MembershipRequestsSearchLayout = parametrize(SearchLayout, {
  roles: communitiesAllRoles,
  appName: appName,
});

const MembershipRequestsSearchBarElement = parametrize(MemberRequestsSearchBarElement, {
  className: "member-requests-searchbar",
  placeholder: i18next.t("Search in membership requests..."),
});

const MembershipRequestsResultItem = parametrize(ResultItem, {
  config: { rolesCanAssign: communitiesRolesCanAssign },
  community: community,
});

const defaultComponents = {
  [`${appName}.SearchApp.layout`]: MembershipRequestsSearchLayout,
  [`${appName}.SearchBar.element`]: MembershipRequestsSearchBarElement,
  [`${appName}.Sort.element`]: DropdownSort,
  [`${appName}.ResultsList.container`]: MembershipRequestsResultsContainer,
  [`${appName}.SearchApp.results`]: MemberRequestsResults,
  [`${appName}.ResultsList.item`]: MembershipRequestsResultItem,
  [`${appName}.EmptyResults.element`]: MembershipRequestsEmptyResults,
  // The RequestModalTriggers are generic enough to be reused here
  "RequestActionModalTrigger.accept": RequestAcceptModalTrigger,
  "RequestActionModalTrigger.decline": RequestDeclineModalTrigger,
  "RequestActionButton.accept": RequestAcceptButton,
  "RequestActionButton.decline": RequestDeclineButton,
  "RequestStatus.layout.submitted": SubmitStatus,
  "RequestStatus.layout.deleted": DeleteStatus,
  "RequestStatus.layout.accepted": AcceptStatus,
  "RequestStatus.layout.declined": DeclineStatus,
  "RequestStatus.layout.cancelled": CancelStatus,
  "RequestStatus.layout.expired": ExpireStatus,
};

const overriddenComponents = overrideStore.getAll();

// Auto-initialize search app
createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents }, // defaultcomponents =
  true, // autoInit =
  "invenio-search-config", // autoInitDataAttr =
  true, // multi =
  MembershipRequestsContextProvider // ContainerComponent =
);
