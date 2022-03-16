/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { DateTime } from "luxon";
import _sample from "lodash/sample";

export function generateInvitations(names) {
  const demoHits = names.map((name, index) => ({
    id: name + index,
    type: "community-invitation",
    status: _sample(pendingStates),
    created_by: {
      community: "test_id",
    },
    topic: {},
    receiver: {
      user: "1",
      name: name,
      description: "CERN",
      links: {
        avatar: "....svg",
      },
    },
    expires_at: DateTime.fromObject({
      year: randomBool() ? 2023 : 2021,
    }).toISO(),

    title: "test invitation",
    number: null,
    is_closed: false,
    is_expired: false,
    role: _sample(roles),
    is_open: false,
    revision_id: 1,
    created: DateTime.now().toISO(),
    updated: DateTime.now().toISO(),

    links: {
      self: "https://127.0.0.1/api/requests/{request_id}",
      actions: {
        cancel: "https://127.0.0.1/api/requests/{request_id}/actions/cancel",
      },
    },
  }));
  return {
    aggregations: {
      visibility: {
        buckets: [],
      },
      role: {
        buckets: [],
      },
    },
    hits: demoHits,
    total: demoHits.length,
  };
}

export const pendingStates = [
  "Pending",
  "Accepted",
  "Declined",
  "Cancelled",
  "Expired",
];

export const sortOptions = ["Expiration", "Best match", "role", "Status"];

export const randomKey = (number) => number * Math.random() * 300;
export const randomBool = () => Math.random() < 0.5;

export const names = [
  "Jane Doe",
  "john Doe",
  "Eric Doe",
  "sophie Doe",
  "Rachel Doe",
  "Diego Diaz",
];

export const roles = [
  {
    title: "owner",
    description: "Full administrative access to the entire community.",
  },
  {
    title: "manager",
    description:
      "Can manage members, curate records and view restricted records",
  },
  {
    title: "curator",
    description: "Can edit and view restricted records",
  },
  {
    title: "reader",
    description: "Can view restricted records",
  },
];

export const filters = [
  {
    key: 130000,
    text: "Status",
    value: "Status",
    options: pendingStates.map((status, index) => ({
      key: randomKey(index),
      text: status,
      value: status.toLowerCase(),
      is_selected: false,
    })),
  },
  {
    key: 120000,
    text: "Role",
    value: "role",
    options: [
      {
        key: 641242140,
        text: "Role",
        value: "role",
        is_selected: false,
      },
    ],
  },
  {
    key: 50000,
    text: "Sort",
    value: "sort",
    options: sortOptions.map((option, index) => ({
      key: randomKey(index),
      text: option,
      value: option.toLowerCase(),
      is_selected: false,
    })),
  },
];
