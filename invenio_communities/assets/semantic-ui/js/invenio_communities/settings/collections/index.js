// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { OverridableContext, overrideStore } from "react-overridable";
import { CollectionsContextProvider } from "../../api/collections/CollectionsContextProvider";
import CollectionTrees from "./CollectionTrees";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const permissions = JSON.parse(domContainer.dataset.permissions);
const overriddenComponents = overrideStore.getAll();

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <CollectionsContextProvider community={community}>
      <CollectionTrees community={community} permissions={permissions} />
    </CollectionsContextProvider>
  </OverridableContext.Provider>,
  domContainer
);
