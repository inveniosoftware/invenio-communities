// This file is part of Invenio-communities
// Copyright (C) 2024 Northwestern University.
//
// Invenio-communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

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

  get userDiscussionUrl() {
    const result = this.url("self_html");
    return result.replace("/requests/", "/me/requests/");
  }
}
