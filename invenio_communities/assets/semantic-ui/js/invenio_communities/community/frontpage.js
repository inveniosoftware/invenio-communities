/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2023 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";

import CommunitiesCardGroup from "./CommunitiesCardGroup";

const userCommunitiesContainer = document.getElementById("user-communities");
const newCommunitiesContainer = document.getElementById("new-communities");

if (userCommunitiesContainer) {
  ReactDOM.render(
    <CommunitiesCardGroup
      fetchDataUrl="/api/user/communities?q=&sort=newest&page=1&size=5"
      emptyMessage="You are not a member of any community."
      defaultLogo="/static/images/square-placeholder.png"
    />,
    userCommunitiesContainer
  );
}

if (newCommunitiesContainer) {
  ReactDOM.render(
    <CommunitiesCardGroup
      fetchDataUrl="/api/communities?q=&sort=newest&page=1&size=5"
      emptyMessage="There are no new communities."
      defaultLogo="/static/images/square-placeholder.png"
    />,
    newCommunitiesContainer
  );
}
