/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { i18next } from "@translations/invenio_communities/i18next";
import _upperFirst from "lodash/upperFirst";

export const MembersSearchBarElement = ({
  placeholder: passedPlaceholder,
  queryString,
  onInputChange,
  executeSearch,
  uiProps,
}) => {
  const placeholder = passedPlaceholder || i18next.t("Search");
  const onBtnSearchClick = () => {
    executeSearch();
  };
  const onKeyPress = (event) => {
    if (event.key === "Enter") {
      executeSearch();
    }
  };
  return (
    <Input
      action={{
        icon: "search",
        onClick: onBtnSearchClick,
        className: "search",
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
};
