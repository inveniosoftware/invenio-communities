// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { bulkMembersSerializer } from "../serializers";
import { CommunityLinksExtractor } from "../CommunityLinksExtractor";
import { http } from "../config";

export class CommunityMembersApi {
  #urls;

  constructor(community, LinksExtractor = CommunityLinksExtractor) {
    this.#urls = new LinksExtractor(community);
  }

  get endpoint() {
    return this.#urls.membersUrl;
  }

  getMembers = async () => {
    return await http.get(this.endpoint);
  };

  deleteMember = async (payload) => {
    return await http.delete(this.endpoint, {
      data: payload,
    });
  };

  updateMembers = async (payload) => {
    return await http.put(this.endpoint, payload);
  };

  updateRole = async (member, role) => {
    const memberSerialized = bulkMembersSerializer([member]);
    const payload = { members: memberSerialized, role: role };
    return await this.updateMembers(payload);
  };

  updateVisibility = async (member, visibility) => {
    const memberSerialized = bulkMembersSerializer([member]);
    const payload = { members: memberSerialized, visible: visibility };
    return await this.updateMembers(payload);
  };

  bulkUpdateRoles = (members, role) => {
    const membersSerialized = bulkMembersSerializer(members);
    const payload = { members: membersSerialized, role: role };
    return this.updateMembers(payload);
  };

  bulkUpdateVisibilities = (members, visibility) => {
    const membersSerialized = bulkMembersSerializer(members);

    const payload = { members: membersSerialized, visible: visibility };
    return this.updateMembers(payload);
  };
}
