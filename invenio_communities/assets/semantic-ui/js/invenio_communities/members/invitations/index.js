/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { InvitationsResults } from "./InvitationsResults";
import { InvitationsSearchBarElement } from "./InvitationsSearchBarElement";
import { InvitationsSearchLayout } from "./InvitationsSearchLayout";
import { InvitationsResultsContainer } from "./InvitationsResultsContainer";
import {InvitationResultItemControlled} from "./InvitationResultItemControlled";

const defaultComponents = {
  "ResultsList.item": InvitationResultItemControlled,
  "SearchApp.layout": InvitationsSearchLayout,
  "SearchBar.element": InvitationsSearchBarElement,
  "SearchApp.results": InvitationsResults,
  "ResultsList.container": InvitationsResultsContainer,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
