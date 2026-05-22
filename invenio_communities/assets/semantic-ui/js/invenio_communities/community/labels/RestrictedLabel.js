/*
 * SPDX-FileCopyrightText: 2023-2024 CERN.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import PropTypes from "prop-types";

import { Label, Icon } from "semantic-ui-react";

export const RestrictedLabel = ({ access }) =>
  access === "restricted" && (
    <Label size="small" horizontal className="negative">
      <Icon name="ban" />
      {i18next.t("Restricted")}
    </Label>
  );

RestrictedLabel.propTypes = {
  access: PropTypes.string.isRequired,
};
