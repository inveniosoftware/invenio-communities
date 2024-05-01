// This file is part of Invenio-communities
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 Northwestern University.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { CommunityLinksExtractor } from "../CommunityLinksExtractor";
import { http } from "react-invenio-forms";

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
}
