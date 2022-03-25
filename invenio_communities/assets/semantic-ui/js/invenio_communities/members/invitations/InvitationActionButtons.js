/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";

export const ActionButtons = ({
  actions,
  onReInvite,
  onView,
  onCancel,
  status,
}) => {
  status = status.toLowerCase();
  const actionsPossible = !_isEmpty(actions);

  const showViewButton = true;
  const showCancel = status === "submitted" && actionsPossible;
  const showReInviteButton = status === "expired" && actionsPossible;

  return (
    <>
      {showReInviteButton && (
        <Button
          size="tiny"
          content={i18next.t("Re invite")}
          onClick={onReInvite}
        />
      )}
      {showViewButton && (
        <Button size="tiny" content={i18next.t("View")} onClick={onView} />
      )}
      {showCancel && (
        <Button size="tiny" content={i18next.t("Cancel")} onClick={onCancel} />
      )}
    </>
  );
};

ActionButtons.propTypes = {
  actions: PropTypes.object.isRequired,
  onReInvite: PropTypes.func,
  onView: PropTypes.func,
  onCancel: PropTypes.func,
  status: PropTypes.string.isRequired,
};
