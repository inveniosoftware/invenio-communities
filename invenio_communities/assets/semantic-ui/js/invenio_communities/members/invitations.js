/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { InvitationsResults } from "./invitations/InvitationsResults";
import { InvitationsSearchBarElement } from "./invitations/InvitationsSearchBarElement";
import { InvitationsSearchLayout } from "./invitations/InvitationsSearchLayout";
import { InvitationsResultsContainer } from "./invitations/InvitationsResultsContainer";
import {InvitationResultItemWithState} from "./invitations/InvitationResultItemWithState";

const defaultComponents = {
  "ResultsList.item": InvitationResultItemWithState,
  "SearchApp.layout": InvitationsSearchLayout,
  "SearchBar.element": InvitationsSearchBarElement,
  "SearchApp.results": InvitationsResults,
  "ResultsList.container": InvitationsResultsContainer,
};

// Auto-initialize search app
createSearchAppInit(defaultComponents);
