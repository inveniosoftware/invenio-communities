// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { http } from "react-invenio-forms";
import { CommunityLinksExtractor } from "../CommunityLinksExtractor";

/**
 * API Client for community collection trees.
 *
 * It mostly uses the API links passed to it from responses.
 *
 */
export class CommunityCollectionsApi {
  #urls;

  constructor(community, LinksExtractor = CommunityLinksExtractor) {
    this.#urls = new LinksExtractor(community);
  }

  get endpoint() {
    return this.#urls.collectionTreesUrl;
  }

  /**
   * Validate tree identifier parameters.
   * @private
   * @param {string|null} treeSlug - Tree slug
   * @param {string|null} treeId - Tree ID
   * @throws {Error} If neither parameter is provided
   */
  _validateTreeIdentifier(treeSlug, treeId) {
    if (!treeSlug && !treeId) {
      throw new Error("Either treeSlug or treeId must be provided");
    }
    if (treeSlug && treeId) {
      console.warn("Both treeSlug and treeId provided; both will be sent to backend");
    }
  }

  /**
   * Build URL with query parameters.
   * @private
   * @param {string} baseUrl - Base URL
   * @param {Object} params - Query parameters to append
   * @returns {string} URL with query parameters
   */
  _buildUrl(baseUrl, params = {}) {
    const url = new URL(baseUrl, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        url.searchParams.set(key, value);
      }
    });
    return url.toString();
  }

  /**
   * List all Community Collection Trees.
   *
   * @param {number} depth - Depth of the collection tree
   * @param {object} options - Custom options
   */
  async get_collection_trees(depth, options) {
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(this.endpoint, { depth });
    return http.get(url, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Create a new Community Collection Tree.
   *
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   */
  async create_collection_trees(payload, options) {
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const collectionTrees = await this.get_collection_trees(10, options);
    let maxOrder = Math.max(
      ...Object.values(collectionTrees.data).map((tree) => tree.order || 0),
      0
    );
    payload.order = maxOrder + 1;
    return http.post(this.endpoint, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Update a Community Collection Tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async update_collection_tree(treeSlug, payload, options, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}`, { tree_id: treeId });
    return http.put(url, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Delete a Community Collection Tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   * @param {boolean} cascade - Delete all collections in the tree (default: false)
   */
  async delete_collection_tree(treeSlug, options, treeId = null, cascade = false) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}`, {
      tree_id: treeId,
      cascade: cascade ? "true" : undefined,
    });
    return http.delete(url, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Get a Community Collection Tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async get_collection_tree(treeSlug, options, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}`, {
      depth: 10,
      tree_id: treeId,
    });
    return http.get(url, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Create a new Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async create_collection(treeSlug, payload, options, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
    };
    const collections = await this.get_collection_tree(treeSlug, options, treeId);
    let maxOrder = Math.max(
      ...Object.values(collections.data.collections).map((tree) => tree.order || 0),
      0
    );
    payload.order = maxOrder + 1;
    const url = this._buildUrl(`${this.endpoint}/${treeSlug}/collections`, {
      tree_id: treeId,
    });
    return http.post(url, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Add a new Community Collection to parent collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the parent collection
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async add_collection(treeSlug, collectionSlug, payload, options, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      { tree_id: treeId }
    );
    return http.post(url, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Update a Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async update_collection(treeSlug, collectionSlug, payload, options, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      { tree_id: treeId }
    );
    return http.put(url, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Delete a Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   * @param {boolean} cascade - Whether to delete child collections (default: false)
   */
  async delete_collection(
    treeSlug,
    collectionSlug,
    options,
    treeId = null,
    cascade = false
  ) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      {
        tree_id: treeId,
        cascade: cascade ? "true" : undefined,
      }
    );
    return http.delete(url, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Get a Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async get_collection(treeSlug, collectionSlug, options, treeId = null) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections/${collectionSlug}`,
      { tree_id: treeId }
    );
    return http.get(url, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Test search query for a Community Collection.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {string} collectionSlug - Slug of the collection
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async test_search_query_for_collection(
    treeSlug,
    collectionSlug,
    payload,
    options,
    treeId = null
  ) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections-records-test`,
      {
        test_col_slug: collectionSlug,
        tree_id: treeId,
      }
    );
    return http.post(url, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Test search query for a Community Base Collection of tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} payload - Serialized Collection object
   * @param {object} options - Custom options
   * @param {string|null} treeId - Tree ID (optional)
   */
  async test_search_query_for_base_collection(
    treeSlug,
    payload,
    options,
    treeId = null
  ) {
    this._validateTreeIdentifier(treeSlug, treeId);
    options = options || {};
    const headers = {
      Accept: "application/json",
    };
    const url = this._buildUrl(
      `${this.endpoint}/${treeSlug}/collections-records-test`,
      { tree_id: treeId }
    );
    return http.post(url, payload, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Batch reorder collection trees.
   *
   * @param {object} orderData - Order data with format: { order: [{slug, order}, ...] }
   * @param {object} options - Custom options
   */
  async batch_reorder_trees(orderData, options = {}) {
    const headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
    };
    const url = `${this.endpoint}/reorder`;
    return http.post(url, orderData, {
      headers: headers,
      ...options,
    });
  }

  /**
   * Batch reorder collections within a tree.
   *
   * @param {string} treeSlug - Slug of the collection tree
   * @param {object} orderData - Order data with format: { order: [{slug, order}, ...] }
   * @param {object} options - Custom options
   */
  async batch_reorder_collections(treeSlug, orderData, options = {}) {
    const headers = {
      "Accept": "application/json",
      "Content-Type": "application/json",
    };
    const url = `${this.endpoint}/${treeSlug}/collections/reorder`;
    return http.post(url, orderData, {
      headers: headers,
      ...options,
    });
  }
}
