/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-FileCopyrightText: 2026 Northwestern University.
 * SPDX-License-Identifier: MIT
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
