/*
 * SPDX-FileCopyrightText: 2024 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import OrganizationsList from "../../organizations/OrganizationsList";

import { RequestMembershipButton } from "./RequestMembershipButton";

const organizationsContainer = document.getElementById("organizations-list");

if (organizationsContainer) {
  const organizations = JSON.parse(organizationsContainer.dataset.organizations);
  const root = createRoot(organizationsContainer);
  root.render(<OrganizationsList organizations={organizations} />);
}

const domContainer = document.getElementById("request-membership-app");

if (domContainer) {
  const community = JSON.parse(domContainer.dataset.community);
  const root = createRoot(domContainer);
  root.render(<RequestMembershipButton community={community} />);
}
