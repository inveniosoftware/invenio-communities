// This file is part of React-Invenio-Deposit
// Copyright (C) 2021 CERN.
// Copyright (C) 2021 Northwestern University.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import axios from "axios";

const apiConfig = {
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
};
const configuredAxios = axios.create(apiConfig);

/**
 * API client response.
 *
 * It's a wrapper/sieve around Axios to contain Axios coupling here. It maps
 * good and bad responses to a unified interface.
 *
 */
export class CommunitiesApiClientResponse {
  constructor(data, errors, code) {
    this.data = data;
    this.errors = errors;
    this.code = code;
  }
}

/**
 * API Client for communities.
 *
 * It mostly uses the API links passed to it from responses.
 *
 */
export class CommunitiesApiClient {
  constructor() {
    this.options = {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    };
  }

  /**
   * Wraps the axios call in a uniform response.
   *
   * @param {function} axios_call - Call to wrap
   */
  async _createResponse(axios_call) {
    try {
      let response = await axios_call();
      return new CommunitiesApiClientResponse(
        response.data,
        response.data.errors,
        response.status
      );
    } catch (error) {
      return new CommunitiesApiClientResponse(
        error.response.data,
        error.response.data.errors,
        error.response.status
      );
    }
  }

  /**
   * Create a new community.
   *
   * @param {object} payload - Serialized community
   * @param {object} options - Custom options
   */
  async create(payload, options) {
    options = options || {};
    return this._createResponse(() =>
      configuredAxios.post("/api/communities", payload, {
        ...this.options,
        ...options,
      })
    );
  }

  /**
   * Update a pre-existing community.
   *
   * @param {string} communityId - identifier
   * @param {object} payload - Serialized community
   * @param {object} options - Custom options
   */
  async update(communityId, payload, options) {
    options = options || {};
    return this._createResponse(() =>
      configuredAxios.put(`/api/communities/${communityId}`, payload, {
        ...this.options,
        ...options,
      })
    );
  }

  /**
   * Delete the community.
   *
   * @param {string} communityId - Identifier
   * @param {object} options - Custom options
   */
  async delete(communityId, options) {
    options = options || {};
    return this._createResponse(() =>
      configuredAxios.delete(`/api/communities/${communityId}`, {
        ...this.options,
        ...options,
      })
    );
  }

  /**
   * Change the identifier of a community.
   *
   * @param {string} communityId - identifier
   * @param {object} newId - Serialized community
   * @param {object} options - Custom options
   */
  async updateId(communityId, newId, options) {
    options = options || {};
    return this._createResponse(() =>
      configuredAxios.post(
        `/api/communities/${communityId}/rename`,
        { id: newId },
        {
          ...this.options,
          ...options,
        }
      )
    );
  }

  /**
   * Update the community logo.
   *
   * @param {string} communityId - Identifier
   * @param {object} payload - File
   * @param {object} options - Custom options
   */
  async updateLogo(communityId, payload, options) {
    options = options || {};
    const headers = {
      ...this.options.headers,
      "Content-Type": "application/octet-stream",
    };
    return this._createResponse(() =>
      configuredAxios.put(`/api/communities/${communityId}/logo`, payload, {
        ...this.options,
        headers: headers,
        ...options,
      })
    );
  }

  /**
   * Delete the community logo.
   *
   * @param {string} communityId - Identifier
   * @param {object} options - Custom options
   */
  async deleteLogo(communityId, options) {
    options = options || {};
    const headers = {
      ...this.options.headers,
      "Content-Type": "application/octet-stream",
    };
    return this._createResponse(() =>
      configuredAxios.delete(`/api/communities/${communityId}/logo`, {
        ...this.options,
        headers: headers,
        ...options,
      })
    );
  }
}
