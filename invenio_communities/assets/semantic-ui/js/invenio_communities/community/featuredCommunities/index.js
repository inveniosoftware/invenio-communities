/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import FeaturedCommunities from "./FeaturedCommunities";

const featuredCommunitiesContainer = document.getElementById("communities-featured");
const columnNumber = featuredCommunitiesContainer.dataset.columnNumber;
const mobileColumnWidth = featuredCommunitiesContainer.dataset.mobileColumnWidth;
const tabletColumnWidth = featuredCommunitiesContainer.dataset.tabletColumnWidth;
const computerColumnWidth = featuredCommunitiesContainer.dataset.computerColumnWidth;
const widescreenColumnWidth =
  featuredCommunitiesContainer.dataset.widescreenColumnWidth;

const root = createRoot(featuredCommunitiesContainer);

root.render(
  <FeaturedCommunities
    columnNumber={columnNumber}
    mobileColumnWidth={mobileColumnWidth}
    computerColumnWidth={computerColumnWidth}
    tabletColumnWidth={tabletColumnWidth}
    widescreenColumnWidth={widescreenColumnWidth}
  />
);
