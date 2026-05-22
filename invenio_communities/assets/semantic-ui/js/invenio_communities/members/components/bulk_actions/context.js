/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";

export const BulkActionsContext = React.createContext({
  bulkActionContext: {},
  addToSelected: () => {},
  allSelected: false,
  setAllSelected: () => {},
  selectedCount: 0,
});
