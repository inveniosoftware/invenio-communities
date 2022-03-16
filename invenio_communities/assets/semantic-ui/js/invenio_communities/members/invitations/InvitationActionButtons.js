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

export const ViewButton = ({ onClick }) => (
  <Button size="tiny" content={i18next.t("View")} onClick={onClick} />
);

export const CancelButton = ({ onClick }) => (
  <Button size="tiny" content={i18next.t("Cancel")} onClick={onClick} />
);

export const ReInviteButton = ({ onClick }) => (
  <Button content={i18next.t("Re invite")} onClick={onClick} />
);

export const ActionButtons = ({ status, onReInvite, onView, onCancel }) => {
  const condition = false;

  if (condition) {
    return <ReInviteButton onClick={() => onReInvite()} />;
  }

  return (
    <>
      <ViewButton onClick={() => onView()} />
      <CancelButton onClick={() => onCancel()} />
    </>
  );
};
