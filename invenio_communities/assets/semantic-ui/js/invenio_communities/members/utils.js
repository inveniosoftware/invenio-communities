/*
 * This file is part of Invenio.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { DateTime } from "luxon";
import _cloneDeep from "lodash/cloneDeep";
import _pick from "lodash/pick";

/**
 * Format given `at` time relative to current time.
 *
 * @export
 * @param {string} at
 * @return {string}
 */
export function formattedTime(at) {
  return DateTime.fromISO(at).setLocale(i18next.language).toRelative();
}

/**
 * Build a "Request" object for the purposes of a controller and own sanity.
 *
 * @export
 * @param {Object} resultItem
 * @param {Array<string>} keysOfActionsLinks
 * @return {Object}
 */
export function buildRequest(resultItem, keysOfActionsLinks) {
  let { request } = resultItem;
  request = _cloneDeep(request);
  request.links = {
    actions: _pick(resultItem.links.actions, keysOfActionsLinks),
  };
  return request;
}
