/*
 * SPDX-FileCopyrightText: 2016-2021 CERN.
 * SPDX-FileCopyrightText: 2023 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import { i18next } from "@translations/invenio_communities/i18next";

import CommunitiesCardGroup from "./CommunitiesCardGroup";

const userCommunitiesContainer = document.getElementById("user-communities");
const newCommunitiesContainer = document.getElementById("new-communities");

if (userCommunitiesContainer) {
  const root = createRoot(userCommunitiesContainer);

  root.render(
    <CommunitiesCardGroup
      fetchDataUrl="/api/user/communities?q=&sort=newest&page=1&size=5"
      emptyMessage={i18next.t("You are not a member of any community.")}
      defaultLogo="/static/images/square-placeholder.png"
    />
  );
}

if (newCommunitiesContainer) {
  const root = createRoot(newCommunitiesContainer);

  root.render(
    <CommunitiesCardGroup
      fetchDataUrl="/api/communities?q=&sort=newest&page=1&size=5"
      emptyMessage={i18next.t("There are no new communities.")}
      defaultLogo="/static/images/square-placeholder.png"
    />
  );
}
