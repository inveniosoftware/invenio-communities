/*
 * SPDX-FileCopyrightText: 2024 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import ReactDOM from "react-dom";
import SubmissionPolicyForm from "./SubmissionPolicyForm";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const formConfig = JSON.parse(domContainer.dataset.formConfig);

ReactDOM.render(
  <SubmissionPolicyForm community={community} formConfig={formConfig} />,
  domContainer
);
