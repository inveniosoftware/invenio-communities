// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
// Copyright (C) 2024-2026 Northwestern University.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CommunityLinksExtractor } from "../CommunityLinksExtractor";
import { http } from "react-invenio-forms";
import { bulkMembersSerializer } from "../serializers";

/**
 * API Client for community membership requests.
 *
 * It mostly uses the API links passed to it from initial community.
 *
 */
export class CommunityMembershipRequestsApi {
  constructor(community) {
    this.community = community;
    this.linksExtractor = new CommunityLinksExtractor(community);
  }

  requestMembership = async (payload) => {
    return await http.post(this.linksExtractor.url("membership_requests"), payload);
  };

  /**
   * Makes a PUT call to resource endpoint to update role of member.
   *
   * That endpoint accepts a bulk update format, so we serialize accordingly.
   *
   * This is an assignment rather than function definition for ease of passing
   * as callback.
   *
   * @param {object} member - member field of search result on Members JSON API
   * @param {string} role - new community role id
   * @returns {axios Response} -
   *
   */
  updateRole = async (member, role) => {
    const payload = {
      members: bulkMembersSerializer([member]),
      role: role,
    };
    return await http.put(this.linksExtractor.url("membership_requests"), payload);
  };
}
