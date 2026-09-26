/*
 * SPDX-FileCopyrightText: 2024 CERN.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import SubmissionPolicyForm from "./SubmissionPolicyForm";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const formConfig = JSON.parse(domContainer.dataset.formConfig);

const root = createRoot(domContainer);
root.render(<SubmissionPolicyForm community={community} formConfig={formConfig} />);
