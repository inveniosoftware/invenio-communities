/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { http } from "react-invenio-forms";

export class GroupsApi {
  get endpoint() {
    return `/api/groups`;
  }

  getGroups = async (query) => {
    return await http.get(`${this.endpoint}?q=${query}`);
  };
}
