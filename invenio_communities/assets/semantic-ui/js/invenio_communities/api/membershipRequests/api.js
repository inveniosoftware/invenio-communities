// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 Northwestern University.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "react-invenio-forms";

import { CommunityLinksExtractor } from "../CommunityLinksExtractor";
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
    // assigned rather than defiend for ease of passing as callback
    return await http.post(this.linksExtractor.url("membership_requests"), payload);
  };

  updateRole = async (membershipRequest, role) => {
    // assigned rather than defiend for ease of passing as callback
    const memberSerialized = bulkMembersSerializer([membershipRequest]);
    const payload = { members: memberSerialized, role: role };
    return await http.put(this.linksExtractor.url("membership_requests"), payload);
  };
}
