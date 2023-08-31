// This file is part of InvenioCommunities
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { FeatureModal } from "./FeatureModal";
import React from "react";
import ReactDOM from "react-dom";
import _get from "lodash/get";
import { OverridableContext, overrideStore } from "react-overridable";
import { FeaturedEntries } from "./featured";
import { AdminDetailsView } from "@js/invenio_administration";

const domContainer = document.getElementById("invenio-details-config");
const title = domContainer.dataset.title;
const fields = JSON.parse(domContainer.dataset.fields);
const pidValue = JSON.parse(domContainer.dataset.pid);
const resourceName = JSON.parse(domContainer.dataset.resourceName);
const displayEdit = JSON.parse(domContainer.dataset.displayEdit);
const displayDelete = JSON.parse(domContainer.dataset.displayDelete);
const actions = JSON.parse(domContainer.dataset.actions);
const apiEndpoint = _get(domContainer.dataset, "apiEndpoint");
const idKeyPath = JSON.parse(_get(domContainer.dataset, "pidPath", "pid"));
const listUIEndpoint = domContainer.dataset.listEndpoint;
const resourceSchema = JSON.parse(domContainer.dataset.resourceSchema);
const uiSchema = JSON.parse(domContainer.dataset?.uiConfig);
const requestHeaders = JSON.parse(domContainer.dataset?.requestHeaders);
const appName = JSON.parse(domContainer.dataset?.appId);

const defaultComponents = {
  [`${appName}.ActionModal.layout`]: FeatureModal,
};

const overriddenComponents = overrideStore.getAll();

domContainer &&
  ReactDOM.render(
    <OverridableContext.Provider
      value={{ ...defaultComponents, ...overriddenComponents }}
    >
      <AdminDetailsView
        title={title}
        actions={actions}
        apiEndpoint={apiEndpoint}
        columns={fields}
        displayEdit={displayEdit}
        displayDelete={displayDelete}
        pid={pidValue}
        idKeyPath={idKeyPath}
        resourceName={resourceName}
        listUIEndpoint={listUIEndpoint}
        resourceSchema={resourceSchema}
        requestHeaders={requestHeaders}
        uiSchema={uiSchema}
        appName={appName}
      >
        <FeaturedEntries />
      </AdminDetailsView>
    </OverridableContext.Provider>,
    domContainer
  );
