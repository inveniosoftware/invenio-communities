/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */
import React from "react";

export const ModalContext = React.createContext({
  closeModal: () => {},
  openModal: () => {},
  modalMode: null,
  modalAction: null,
  modalOpen: false,
});
