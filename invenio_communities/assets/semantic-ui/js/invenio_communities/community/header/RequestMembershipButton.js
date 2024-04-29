/*
 * This file is part of Invenio.
 * Copyright (C) 2024 CERN.
 * Copyright (C) 2024 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { Formik } from "formik";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { TextAreaField } from "react-invenio-forms";
import { Button, Form, Modal } from "semantic-ui-react";

export function RequestMembershipModal(props) {
  const { isOpen, onClose } = props;

  const onSubmit = async (values, { setSubmitting, setFieldError }) => {
    // TODO: implement me
    console.log("RequestMembershipModal.onSubmit(args) called");
    console.log("TODO: implement me", arguments);
  };

  let confirmed = true;

  return (
    <Formik
      initialValues={{
        requestMembershipComment: "",
      }}
      onSubmit={onSubmit}
    >
      {({ values, isSubmitting, handleSubmit }) => (
        <Modal
          open={isOpen}
          onClose={onClose}
          size="small"
          closeIcon
          closeOnDimmerClick={false}
        >
          <Modal.Header>{i18next.t("Request Membership")}</Modal.Header>
          <Modal.Content>
            <Form>
              <TextAreaField
                fieldPath="requestMembershipComment"
                label={i18next.t("Message to managers (optional)")}
              />
            </Form>
          </Modal.Content>
          <Modal.Actions>
            <Button onClick={onClose} floated="left">
              {i18next.t("Cancel")}
            </Button>
            <Button
              onClick={(event) => {
                // TODO: Implement me
                console.log("RequestMembershipModal button clicked.");
              }}
              positive={confirmed}
              primary
            >
              {i18next.t("Request Membership")}
            </Button>
          </Modal.Actions>
        </Modal>
      )}
    </Formik>
  );
}

RequestMembershipModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export function RequestMembershipButton(props) {
  const [isModalOpen, setModalOpen] = useState(false);

  const handleClick = () => {
    setModalOpen(true);
  };

  const handleClose = () => {
    setModalOpen(false);
  };

  return (
    <>
      <Button
        name="request-membership"
        onClick={handleClick}
        positive
        icon="sign-in"
        labelPosition="left"
        content={i18next.t("Request Membership")}
      />
      {isModalOpen && (
        <RequestMembershipModal isOpen={isModalOpen} onClose={handleClose} />
      )}
    </>
  );
}
