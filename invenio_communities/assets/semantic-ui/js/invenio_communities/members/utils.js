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
 * This means extracting the request-related data from the Member object
 * and repackaging them like a Request object expected by Request components.
 * Member objects are members, invitations and membership requests.
 *
 * @export
 * @param {Object} member - search result on Members JSON API
 * @param {Array<string>} keysOfActionsLinks
 * @return {Object}
 */
export function buildRequestFromMember(member, keysOfActionsLinks) {
  let request = _cloneDeep(member.request);
  request.links = {
    actions: _pick(member.links.actions, keysOfActionsLinks),
  };
  return request;
}
