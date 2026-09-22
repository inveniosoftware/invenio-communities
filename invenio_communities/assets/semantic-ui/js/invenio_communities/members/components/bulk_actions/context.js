/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { createContext } from "react";

export const BulkActionsContext = createContext({
  bulkActionContext: {},
  addToSelected: () => {},
  allSelected: false,
  setAllSelected: () => {},
  selectedCount: 0,
});
