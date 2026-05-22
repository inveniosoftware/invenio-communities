/*
 * SPDX-FileCopyrightText: 2022-2024 CERN.
 * SPDX-FileCopyrightText: 2024 Northwestern University.
 * SPDX-License-Identifier: MIT
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
