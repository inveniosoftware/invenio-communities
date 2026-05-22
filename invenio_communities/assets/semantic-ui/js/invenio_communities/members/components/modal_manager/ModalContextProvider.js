/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import React, { Component } from "react";
import { ModalContext } from "./index";
import PropTypes from "prop-types";

export class ModalContextProvider extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalMode: null,
      modalAction: null,
      modalOpen: false,
      member: null,
    };
  }

  openModal = ({ modalAction, modalMode, member }) => {
    this.setState({ modalOpen: true, modalAction, modalMode, member });
  };

  closeModal = () => {
    this.setState({ modalOpen: false });
  };

  render() {
    const { children } = this.props;
    const { modalMode, modalAction, modalOpen, member } = this.state;

    return (
      <ModalContext.Provider
        value={{
          closeModal: this.closeModal,
          openModal: this.openModal,
          modalMode,
          modalAction,
          modalOpen,
          member,
        }}
      >
        {children}
      </ModalContext.Provider>
    );
  }
}

ModalContextProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
