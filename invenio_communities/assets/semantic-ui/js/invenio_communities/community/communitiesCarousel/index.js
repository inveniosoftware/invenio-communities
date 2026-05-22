/*
 * SPDX-FileCopyrightText: 2016-2024 CERN.
 * SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import ReactDOM from "react-dom";
import { OverridableContext, overrideStore } from "react-overridable";
import CommunitiesCarousel from "./CommunitiesCarousel";

const communitiesCarouselContainer = document.getElementById("communities-carousel");
const title = communitiesCarouselContainer.dataset.title;
const fetchUrl = communitiesCarouselContainer.dataset.fetchUrl;
const intervalDelay = parseInt(communitiesCarouselContainer.dataset.intervalDelay);
const animationSpeed = parseInt(communitiesCarouselContainer.dataset.animationSpeed);
const defaultLogo = communitiesCarouselContainer.dataset.defaultLogo;
const itemsPerPage = communitiesCarouselContainer.dataset.itemsPerPage;
const showUploadBtn = JSON.parse(communitiesCarouselContainer.dataset.showUploadBtn);

const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CommunitiesCarousel
      title={title}
      fetchUrl={fetchUrl}
      intervalDelay={intervalDelay}
      animationSpeed={animationSpeed}
      defaultLogo={defaultLogo}
      itemsPerPage={itemsPerPage}
      showUploadBtn={showUploadBtn}
    />
  </OverridableContext.Provider>,
  communitiesCarouselContainer
);
