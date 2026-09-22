/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import { createContext } from "react";

export const ModalContext = createContext({
  closeModal: () => {},
  openModal: () => {},
  modalMode: null,
  modalAction: null,
  modalOpen: false,
});
