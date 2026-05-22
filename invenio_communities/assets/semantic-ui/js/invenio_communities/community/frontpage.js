/*
 * SPDX-FileCopyrightText: 2016-2021 CERN.
 * SPDX-FileCopyrightText: 2023 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import ReactDOM from "react-dom";
import { i18next } from "@translations/invenio_communities/i18next";

import CommunitiesCardGroup from "./CommunitiesCardGroup";

const userCommunitiesContainer = document.getElementById("user-communities");
const newCommunitiesContainer = document.getElementById("new-communities");

if (userCommunitiesContainer) {
  ReactDOM.render(
    <CommunitiesCardGroup
      fetchDataUrl="/api/user/communities?q=&sort=newest&page=1&size=5"
      emptyMessage={i18next.t("You are not a member of any community.")}
      defaultLogo="/static/images/square-placeholder.png"
    />,
    userCommunitiesContainer
  );
}

if (newCommunitiesContainer) {
  ReactDOM.render(
    <CommunitiesCardGroup
      fetchDataUrl="/api/communities?q=&sort=newest&page=1&size=5"
      emptyMessage={i18next.t("There are no new communities.")}
      defaultLogo="/static/images/square-placeholder.png"
    />,
    newCommunitiesContainer
  );
}
