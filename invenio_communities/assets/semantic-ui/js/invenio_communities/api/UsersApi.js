/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { http } from "react-invenio-forms";

export class UsersApi {
  get endpoint() {
    return `/api/users`;
  }

  getUsers = async (query) => {
    return await http.get(`${this.endpoint}?q=${query}`);
  };

  suggestUsers = async (query) => {
    return await http.get(`${this.endpoint}?suggest=${query}`);
  };
}
