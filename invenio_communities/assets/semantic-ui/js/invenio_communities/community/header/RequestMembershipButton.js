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
import { Button, Form, Grid, Message, Modal } from "semantic-ui-react";

import { CommunityMembershipRequestsApi } from "../../api/membershipRequests/api";
import { communityErrorSerializer } from "../../api/serializers";
import { RequestLinksExtractor } from "../../api/RequestLinksExtractor";

export function RequestMembershipModal(props) {
  const [errorMsg, setErrorMsg] = useState("");

  const { community, isOpen, onClose } = props;

  const onSubmit = async (values, { setSubmitting, setFieldError }) => {
    /**Submit callback called from Formik. */
    setSubmitting(true);

    const client = new CommunityMembershipRequestsApi(community);

    try {
      const response = await client.requestMembership(values);
      const linksExtractor = new RequestLinksExtractor(response.data);
      window.location.href = linksExtractor.userDiscussionUrl;
    } catch (error) {
      setSubmitting(false);

      console.log("Error");
      console.dir(error);

      const { errors, message } = communityErrorSerializer(error);

      if (message) {
        setErrorMsg(message);
      }

      if (errors) {
        errors.forEach(({ field, messages }) => setFieldError(field, messages[0]));
      }
    }
  };

  return (
    <Formik
      initialValues={{
        message: "",
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
            <Message hidden={errorMsg === ""} negative className="flashed">
              <Grid container>
                <Grid.Column mobile={16} tablet={12} computer={8} textAlign="left">
                  <strong>{errorMsg}</strong>
                </Grid.Column>
              </Grid>
            </Message>

            <Form>
              <TextAreaField
                fieldPath="message"
                label={i18next.t("Message to managers (optional)")}
              />
            </Form>
          </Modal.Content>
          <Modal.Actions>
            <Button onClick={onClose} floated="left">
              {i18next.t("Cancel")}
            </Button>
            <Button
              disabled={isSubmitting}
              loading={isSubmitting}
              onClick={handleSubmit}
              positive
              primary
              type="button"
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
  community: PropTypes.object.isRequired,
};

export function RequestMembershipButton(props) {
  const [isModalOpen, setModalOpen] = useState(false);
  const { community } = props;

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
        <RequestMembershipModal
          isOpen={isModalOpen}
          onClose={handleClose}
          community={community}
        />
      )}
    </>
  );
}

RequestMembershipButton.propTypes = {
  community: PropTypes.object.isRequired,
};
