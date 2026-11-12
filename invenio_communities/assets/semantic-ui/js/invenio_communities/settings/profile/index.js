/*
 * SPDX-FileCopyrightText: 2016-2023 CERN.
 * SPDX-FileCopyrightText: 2021-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import { default as CommunityProfileForm } from "./CommunityProfileForm";
import { OverridableContext, overrideStore } from "react-overridable";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const types = JSON.parse(domContainer.dataset.types);
const logoMaxSize = JSON.parse(domContainer.dataset.logoMaxSize);
const customFields = JSON.parse(domContainer.dataset.customFields);
const permissions = JSON.parse(domContainer.dataset.permissions);
const overriddenComponents = overrideStore.getAll();

const root = createRoot(domContainer);

root.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CommunityProfileForm
      community={community}
      types={types}
      logoMaxSize={logoMaxSize}
      customFields={customFields}
      permissions={permissions}
    />
  </OverridableContext.Provider>
);
