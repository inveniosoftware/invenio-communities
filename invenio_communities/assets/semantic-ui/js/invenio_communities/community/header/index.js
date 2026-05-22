/*
 * SPDX-FileCopyrightText: 2024 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import ReactDOM from "react-dom";
import OrganizationsList from "../../organizations/OrganizationsList";
import React from "react";

import { RequestMembershipButton } from "./RequestMembershipButton";

const organizationsContainer = document.getElementById("organizations-list");

if (organizationsContainer) {
  const organizations = JSON.parse(organizationsContainer.dataset.organizations);
  ReactDOM.render(
    <OrganizationsList organizations={organizations} />,
    organizationsContainer
  );
}

const domContainer = document.getElementById("request-membership-app");

if (domContainer) {
  const community = JSON.parse(domContainer.dataset.community);
  ReactDOM.render(<RequestMembershipButton community={community} />, domContainer);
}
