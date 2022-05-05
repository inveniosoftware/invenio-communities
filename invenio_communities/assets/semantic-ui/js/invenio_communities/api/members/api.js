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

  removeMemberBase = async (payload) => {
    return await http.delete(this.endpoint, {
      data: payload,
    });
  };

  removeMember = async ({ type, id }) => {
    const payload = {
      members: [{ type, id }],
    };

    return this.removeMemberBase(payload);
  };

  bulkRemoveMembers = async (members) => {
    const memberSerialized = bulkMembersSerializer(members);

    return this.removeMemberBase({ members: memberSerialized });
  };

  updateMembers = async ({ payload, refresh = false } = {}) => {
    const url = new URL(this.endpoint);
    const params = new URLSearchParams();
    refresh && params.append("refresh", refresh);
    return await http.put(`${url}?${params.toString()}`, payload);
  };

  updateRole = async (member, role) => {
    const memberSerialized = bulkMembersSerializer([member]);
    const payload = { members: memberSerialized, role: role };
    return await this.updateMembers({ payload: payload });
  };

  updateVisibility = async (member, visibility) => {
    const memberSerialized = bulkMembersSerializer([member]);
    const payload = { members: memberSerialized, visible: visibility };
    return await this.updateMembers({ payload: payload });
  };

  bulkUpdateRoles = (members, role) => {
    const membersSerialized = bulkMembersSerializer(members);
    const payload = { members: membersSerialized, role: role };
    return this.updateMembers({ payload: payload, refresh: true });
  };

  bulkUpdateVisibilities = (members, visibility) => {
    const membersSerialized = bulkMembersSerializer(members);

    const payload = { members: membersSerialized, visible: visibility };
    return this.updateMembers({ payload: payload, refresh: true });
  };
}
