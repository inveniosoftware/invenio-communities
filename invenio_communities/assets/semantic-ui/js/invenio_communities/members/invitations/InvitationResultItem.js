/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { DateTime } from "luxon";
import {
  Table,
  Grid,
  Container,
  List,
  Icon,
  Loader, Dropdown,
} from 'semantic-ui-react';
import { Image } from "react-invenio-forms";
import { ActionButtons } from "./InvitationActionButtons";
import PropTypes from "prop-types";
import { ErrorPopup } from "../components/ErrorPopup";
import { i18next } from "@translations/invenio_communities/i18next";
import { SuccessIcon } from "../components/SuccessIcon";
import _sample from "lodash/sample";

const dropdownOptionsGenerator = (value) => {
  return Object.entries(value).map(([key, settings]) => {
    return {
      key: key,
      text: settings.title,
      value: key,
      content: (
        <List>
          <List.Item>
            <List.Content>
              <List.Header>{settings.title}</List.Header>
              <List.Description>{settings.description}</List.Description>
            </List.Content>
          </List.Item>
        </List>
      ),
    };
  });
};

const formattedTime = (expires_at) =>
  DateTime.fromISO(expires_at).setLocale(i18next.language).toRelative();

export const InvitationResultItem = ({
  invitation,
  onRoleChange,
  isLoading,
  error,
  success,
  onSuccessTimeOut,
  onErrorClose,
  roles,
  onView,
  onReInvite,
  onCancel,
}) => {
  const { receiver, status, expires_at, links } = invitation;

  return (
    <Table.Row className="community-member-item">
      <Table.Cell>
        <Grid textAlign="left" verticalAlign="middle">
          <Grid.Column width={4}>
            <Image src={"/abc"} avatar circular />
          </Grid.Column>
          <Grid.Column width={12}>
            <List>
              <List.Item as="a">{receiver.name || receiver.user}</List.Item>
            </List>
          </Grid.Column>
        </Grid>
      </Table.Cell>
      <Table.Cell>{status}</Table.Cell>
      <Table.Cell>
        <Grid>
          <Grid.Row>
            <Grid.Column width={13} verticalAlign="middle">
              {formattedTime(expires_at)}
            </Grid.Column>
            <Grid.Column width={3} textAlign="right">
              {isLoading && <Loader active inline="centered" size="small" />}
              <SuccessIcon
                success={success}
                timeOutDelay={4000}
                onTimeOut={onSuccessTimeOut}
              />
              <ErrorPopup
                onClose={onErrorClose}
                error={error}
                trigger={<Icon name="exclamation circle" className="error" />}
              />
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Table.Cell>
      <Table.Cell>
      <Dropdown
        options={dropdownOptionsGenerator(roles)}
        selection
        fluid
        // TODO - replace with role added to invitation payload
        value="curator"
        openOnFocus={false}
        selectOnBlur={false}
        onChange={(e, { value: role }) => {
            onRoleChange(role);
          }}
      />
      </Table.Cell>
      <Table.Cell>
        <Container fluid textAlign="right">
          <ActionButtons
            actions={links.actions}
            onCancel={onCancel}
            onReInvite={onReInvite}
            onView={onView}
            status={status}
          />
        </Container>
      </Table.Cell>
    </Table.Row>
  );
};

InvitationResultItem.propTypes = {
  invitation: PropTypes.object.isRequired,
  onRoleChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  error: PropTypes.string,
  success: PropTypes.bool,
  onErrorClose: PropTypes.func,
  onSuccessTimeOut: PropTypes.func,
  onCancel: PropTypes.func.isRequired,
  onReInvite: PropTypes.func.isRequired,
  onView: PropTypes.func.isRequired,
  roles: PropTypes.object.isRequired,
};

InvitationResultItem.defaultProps = {
  isLoading: false,
  error: "",
  success: false,
  onErrorClose: () => null,
  onSuccessTimeOut: () => null,
};
