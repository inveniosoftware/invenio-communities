/*
 * SPDX-FileCopyrightText: 2023 CERN.
 * SPDX-FileCopyrightText: 2024 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import CommunityPrivilegesForm from "./CommunityPrivilegesForm";

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const community = JSON.parse(domContainer.dataset.community);

const root = createRoot(domContainer);
root.render(<CommunityPrivilegesForm formConfig={formConfig} community={community} />);
