// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from './config';
import _sample from "lodash/sample";

export class CommunityInvitationsApi {
  #links;

  constructor(links) {
    this.#links = links;
  }

  createInvite = async (community_id, payload) => {
    const endpoint = `/api/communities/${community_id}/invitations`;
    return await http.post(endpoint, payload);
  };

  updateInvite = async (request_id, payload) => {
    // TODO invitation service missing
    const endpoint = `/api/requests/${request_id}`;
    return await http.put(endpoint, payload);
  };

  updateRole = async (role, request) => {
    // TODO invitation service missing
    const updatedItem = { ...request, role };

    function mockedRole() {
      return { role: "manager" };
    }

    function mockedError() {
      return { message: "Unknown error. Could not change role."}
    }

    const mockCall = new Promise(function(resolve, reject){
      if(_sample([true, false])) {
          return resolve(mockedRole());
      }else{
          return reject(mockedError());
      }
    })

    return await mockCall;

  };
}
