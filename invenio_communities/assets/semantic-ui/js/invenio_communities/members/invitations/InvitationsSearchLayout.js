/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Button } from "semantic-ui-react";
import { SearchAppResultsPane } from "@js/invenio_search_ui/components";
import { SearchBarWithFiltersWithState } from "../components/SearchBarWithFilters";
import { i18next } from "@translations/invenio_communities/i18next";

export const InvitationsSearchLayout = ({ config, updateQueryState }) => {
  const sortOptions = config.sortOptions;

  return (
    <>
      <SearchBarWithFiltersWithState
        sortOptions={sortOptions}
        updateQueryState={updateQueryState}
        customCmp={
          <Button
            content={i18next.t("Invite members")}
            positive
            size="tiny"
            className="ml-10"
            compact
          />
        }
      />
      <SearchAppResultsPane layoutOptions={config.layoutOptions} />
    </>
  );
};
