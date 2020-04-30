// This file is part of Invenio
// Copyright (C) 2020 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

export { ResultsGridItemTemplate } from "./ResultsGridItemTemplate"
export { ResultsItemTemplate } from "./ResultsItemTemplate"

const aggregations = [
  {
    title: "Types",
    agg: {
      field: "type",
      aggName: "type"
    }
  },
  {
    title: "Domains",
    agg: {
      field: "domain",
      aggName: "domain"
    }
  }
];

const sortValues = [
  {
    text: "Best match",
    sortBy: "bestmatch",
    sortOrder: "desc",
    defaultOnEmptyString: true
  },
  {
    text: "Newest",
    sortBy: "mostrecent",
    sortOrder: "asc",
    default: true
  },
  {
    text: "Oldest",
    sortBy: "mostrecent",
    sortOrder: "desc"
  }
];

const resultsPerPageValues = [
  {
    text: "10",
    value: 10
  },
  {
    text: "20",
    value: 20
  },
  {
    text: "50",
    value: 50
  }
];


const searchApi = {
  baseURL: "",
  url: "/api/records",
  timeout: 5000
};

export const config = {
  searchApi,
  aggregations,
  sortValues,
  resultsPerPageValues
};
