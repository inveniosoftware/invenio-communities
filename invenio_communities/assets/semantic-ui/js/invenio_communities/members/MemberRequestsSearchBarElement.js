/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";

export const MemberRequestsSearchBarElement = ({
  onBtnSearchClick,
  onInputChange,
  onKeyPress,
  queryString,
  uiProps,
  className,
  placeholder,
}) => {
  return (
    <Input
      className={className}
      action={{
        icon: "search",
        onClick: onBtnSearchClick,
        className: "search",
        title: i18next.t("Search"),
      }}
      fluid
      placeholder={placeholder}
      onChange={(_, { value }) => {
        onInputChange(value);
      }}
      value={queryString}
      onKeyPress={onKeyPress}
      {...uiProps}
    />
  );
};

MemberRequestsSearchBarElement.propTypes = {
  onBtnSearchClick: PropTypes.func.isRequired,
  onInputChange: PropTypes.func.isRequired,
  onKeyPress: PropTypes.func.isRequired,
  queryString: PropTypes.string.isRequired,
  uiProps: PropTypes.object,
  className: PropTypes.string,
  placeholder: PropTypes.string,
};

MemberRequestsSearchBarElement.defaultProps = {
  uiProps: null,
  className: "",
  placeholder: "",
};
