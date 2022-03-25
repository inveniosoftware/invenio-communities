// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "./config";

export class CommunityMembersApi {
  constructor(community_id) {
    this.community_id = community_id;
  }

  get endpoint() {
    return `/api/communities/${this.community_id}/members`;
  }

  getMembers = async () => {
    return await http.get(this.endpoint);
  };

  deleteMember = async (payload) => {
    return await http.delete(this.endpoint, {
      data: payload,
    });
  };

  updateMember = async (payload) => {
    return await http.put(this.endpoint, payload);
  };
}
