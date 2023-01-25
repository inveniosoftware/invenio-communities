// This file is part of InvenioCommunities
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { initDefaultSearchComponents } from "@js/invenio_administration";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { FeatureModal } from "./FeatureModal";
import { parametrize, overrideStore } from "react-overridable";
import { NotificationController, BoolFormatter } from "@js/invenio_administration";

const domContainer = document.getElementById("invenio-search-config");

const appName = "InvenioCommunities.AdministrationListView";

const defaultComponents = initDefaultSearchComponents(domContainer, appName);
const CustomBoolFormatter = parametrize(BoolFormatter, {
  icon: "star",
  color: "yellow",
});

const overriddenDefaultComponents = {
  ...defaultComponents,
  [`${appName}.BoolFormatter`]: CustomBoolFormatter,
  [`${appName}.ActionModal.layout`]: FeatureModal,
};

const overriddenComponents = overrideStore.getAll();

createSearchAppInit(
  { ...overriddenDefaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true,
  NotificationController
);
