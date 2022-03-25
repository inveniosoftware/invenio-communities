// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "./config";

export class CommunityInvitationsApi {
  createInvite = async (community_id, payload) => {
    const endpoint = `/api/communities/${community_id}/invitations`;
    return await http.post(endpoint, payload);
  };

  updateInvite = async (request_id, payload) => {
    const endpoint = `/api/requests/${request_id}`;
    return await http.put(endpoint, payload);
  };

  updateRole = async (role, request) => {
    const updatedItem = { ...request, role };

    return this.updateInvite(request.id, updatedItem);
  };
}

export class CommunityActionsApi {
  #links;

  constructor(links) {
    this.#links = links;
  }

  declineAction = async (payload) => {
    return await http.post(this.#links.actions.decline, { payload: payload });
  };
}
