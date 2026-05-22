/*
 * SPDX-FileCopyrightText: 2023 CERN.
 * SPDX-License-Identifier: MIT
 */

import _get from "lodash/get";

const APIRoutesGenerators = {
  delete: (record, idKeyPath = "id") => {
    return `/api/communities/${_get(record, idKeyPath)}`;
  },
  restore: (record, idKeyPath = "id") => {
    return `/api/communities/${_get(record, idKeyPath)}/restore`;
  },
};

export const APIRoutes = {
  ...APIRoutesGenerators,
};
