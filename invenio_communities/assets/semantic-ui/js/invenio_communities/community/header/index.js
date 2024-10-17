/*
 * This file is part of Invenio.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import ReactDOM from "react-dom";
import OrganizationsList from "../../organizations/OrganizationsList";
import React from "react";

import { RequestMembershipButton } from "./RequestMembershipButton";

const organizationsContainer = document.getElementById("organizations-list");
const organizations = JSON.parse(organizationsContainer.dataset.organizations);

if (organizationsContainer) {
  ReactDOM.render(
    <OrganizationsList organizations={organizations} />,
    organizationsContainer
  );
}

const domContainer = document.getElementById("request-membership-app");

const community = JSON.parse(domContainer.dataset.community);

if (domContainer) {
  ReactDOM.render(<RequestMembershipButton community={community} />, domContainer);
}
