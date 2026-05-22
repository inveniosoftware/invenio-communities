/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { initDefaultSearchComponents } from "@js/invenio_administration";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { RecordSearchLayout } from "./search/RecordSearchLayout";
import { FeatureModal } from "./FeatureModal";
import { parametrize } from "react-overridable";
import { NotificationController, BoolFormatter } from "@js/invenio_administration";
import { RecordResourceActions } from "./components/RecordResourceActions";

const domContainer = document.getElementById("invenio-search-config");

const defaultComponents = initDefaultSearchComponents(domContainer);
const CustomBoolFormatter = parametrize(BoolFormatter, {
  icon: "star",
  color: "yellow",
});

const overridenComponents = {
  ...defaultComponents,
  "InvenioAdministration.BoolFormatter": CustomBoolFormatter,
  "InvenioAdministration.ActionModal.feature": FeatureModal,
  "InvenioAdministration.ResourceActions": RecordResourceActions,
  "SearchApp.layout": RecordSearchLayout,
};

createSearchAppInit(
  overridenComponents,
  true,
  "invenio-search-config",
  false,
  NotificationController
);
