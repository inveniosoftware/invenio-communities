/*
 * This file is part of Invenio.
 * Copyright (C) 2022-2024 CERN.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { withState } from "react-searchkit";

export const MembersSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    updateQueryState,
    currentQueryState,
    uiProps,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search in members ...");
    const onSearch = () => {
      updateQueryState({ ...currentQueryState, queryString });
    };
    const onBtnSearchClick = () => {
      onSearch();
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        onSearch();
      }
    };
    return (
      <Input
        action={{
          icon: "search",
          onClick: onBtnSearchClick,
          className: "search",
          title: i18next.t("Search"),
        }}
        fluid
        placeholder={placeholder}
        onChange={(event, { value }) => {
          onInputChange(value);
        }}
        value={queryString}
        onKeyPress={onKeyPress}
        {...uiProps}
      />
    );
  }
);
