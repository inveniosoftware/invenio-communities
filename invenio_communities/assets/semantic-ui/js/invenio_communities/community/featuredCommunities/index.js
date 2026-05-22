/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import ReactDOM from "react-dom";
import FeaturedCommunities from "./FeaturedCommunities";

const featuredCommunitiesContainer = document.getElementById("communities-featured");
const columnNumber = featuredCommunitiesContainer.dataset.columnNumber;
const mobileColumnWidth = featuredCommunitiesContainer.dataset.mobileColumnWidth;
const tabletColumnWidth = featuredCommunitiesContainer.dataset.tabletColumnWidth;
const computerColumnWidth = featuredCommunitiesContainer.dataset.computerColumnWidth;
const widescreenColumnWidth =
  featuredCommunitiesContainer.dataset.widescreenColumnWidth;

ReactDOM.render(
  <FeaturedCommunities
    columnNumber={columnNumber}
    mobileColumnWidth={mobileColumnWidth}
    computerColumnWidth={computerColumnWidth}
    tabletColumnWidth={tabletColumnWidth}
    widescreenColumnWidth={widescreenColumnWidth}
  />,
  featuredCommunitiesContainer
);
