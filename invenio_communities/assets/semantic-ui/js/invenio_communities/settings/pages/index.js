/*
 * SPDX-FileCopyrightText: 2023 CERN.
 * SPDX-License-Identifier: MIT
 */

import { createRoot } from "react-dom/client";
import { CommunityPagesForm } from "./CommunityPagesForm";

const domContainer = document.getElementById("community-settings-pages");
const community = JSON.parse(domContainer.dataset.community);

const root = createRoot(domContainer);
root.render(<CommunityPagesForm community={community} />);
