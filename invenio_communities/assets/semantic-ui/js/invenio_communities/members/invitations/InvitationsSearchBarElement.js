/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

export const InvitationsSearchBarElement = ({
  actionProps,
  onBtnSearchClick,
  onInputChange,
  onKeyPress,
  overridableId,
  placeholder,
  queryString,
  uiProps
}) => {


  return (
    <Input
      action={{
        icon: "search",
        onClick: onBtnSearchClick,
        className: "search",
      }}
      fluid
      {...uiProps}
      placeholder={i18next.t("Search in invitations...")}
      onChange={(_, { value }) => {
        onInputChange(value);
      }}
      value={queryString}
      onKeyPress={onKeyPress}
      {...uiProps}
    />
  );
};
