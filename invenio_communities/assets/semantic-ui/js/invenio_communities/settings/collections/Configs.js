// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_communities/i18next";
import * as Yup from "yup";

export const COLLECTION_VALIDATION_SCHEMA = Yup.object({
  title: Yup.string()
    .required(i18next.t("Title is required"))
    .max(255, i18next.t("Maximum number of characters is 255")),
  slug: Yup.string()
    .required(i18next.t("Slug is required"))
    .max(100, i18next.t("Maximum number of characters is 100")),
  search_query: Yup.string().required(i18next.t("Search query is required")),
  order: Yup.number(),
});

export const COLLECTION_TREE_VALIDATION_SCHEMA = Yup.object({
  title: Yup.string()
    .required(i18next.t("Title is required"))
    .max(255, i18next.t("Maximum number of characters is 255")),
  slug: Yup.string()
    .required(i18next.t("Slug is required"))
    .max(100, i18next.t("Maximum number of characters is 100")),
});

export const generateSlug = (text) => {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-")
    .replace(/&/g, "-and-")
    .replace(/[^\w\-]+/g, "")
    .replace(/\-\-+/g, "-");
};
