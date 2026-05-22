/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import React, { Component } from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { RequestActionContext } from "@js/invenio_requests";

export class ActionButtons extends Component {
  static contextType = RequestActionContext;

  render() {
    const { linkExtractor } = this.context;
    return (
      <Button
        as="a"
        target="_blank"
        size="medium"
        content={i18next.t("View")}
        href={linkExtractor.self_html}
      />
    );
  }
}

ActionButtons.propTypes = {};
