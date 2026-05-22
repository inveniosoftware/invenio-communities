/*
 * SPDX-FileCopyrightText: 2024 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

export class RequestLinksExtractor {
  #urls;

  constructor(request) {
    if (!request?.links) {
      throw TypeError("Request resource links are undefined");
    }
    this.#urls = request.links;
  }

  url(key) {
    const urlOfKey = this.#urls[key];
    if (!urlOfKey) {
      throw TypeError(`"${key}" link missing from resource.`);
    }
    return urlOfKey;
  }
}
