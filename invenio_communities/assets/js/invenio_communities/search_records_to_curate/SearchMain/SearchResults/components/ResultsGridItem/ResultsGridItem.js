// This file is part of InvenioRDM
// Copyright (C) 2020 CERN.
// Copyright (C) 2020 Northwestern University.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useContext } from "react";
import { ResultsGrid } from "react-searchkit";
import { SearchComponentsContext } from "../../../SearchMain";

export const ResultsGridItem = () => {
  const { ResultsGridItem } = useContext(SearchComponentsContext)
  return (
    <ResultsGrid renderGridItem={ResultsGridItem} />
  );
}
