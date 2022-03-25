/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { randomKey, roles, randomBool } from "../mock";
import { DateTime } from "luxon";
import { Table, Grid, Container, List, Icon, Loader } from "semantic-ui-react";
import { Image } from "react-invenio-forms";
import { ActionButtons } from "./InvitationActionButtons";
import PropTypes from "prop-types";
import { ErrorPopup } from "../components/ErrorPopup";
import { i18next } from "@translations/invenio_communities/i18next";
import { MemberDropdown } from "../components/Dropdowns";
import { SuccessIcon } from "../components/SuccessIcon";
import _sample from "lodash/sample";

const RoleContent = ({ title, description }) => (
  <List>
    <List.Item>
      <List.Content>
        <List.Header>{title}</List.Header>
        <List.Description>{description}</List.Description>
      </List.Content>
    </List.Item>
  </List>
);

const RoleSelection = ({ initialValue, onChange, status }) => {
  if (status !== "submitted") {
    return initialValue;
  }

  const options = roles.map(({ title, description }, index) => ({
    key: randomKey(index),
    text: title,
    value: title.toLowerCase(),
    is_selected: initialValue === title,
    content: <RoleContent title={title} description={description} />,
  }));

  return (
    <MemberDropdown
      updateMember={onChange}
      initialValue={initialValue}
      options={options}
    />
  );
};

const formattedTime = (expires_at) =>
  DateTime.fromISO(expires_at).setLocale(i18next.language).toRelative();

export const InvitationResultItem = ({
  invitation,
  onRoleChange,
  isLoading,
  key,
  error,
  success,
  onSuccessTimeOut,
  onErrorClose,
  onView,
  onReInvite,
  onCancel,
}) => {
  const { receiver, status, expires_at, links } = invitation;

  const role = _sample(roles);

  const avatar = links.avatar || "/static/images/square-placeholder.png";

  return (
    <Table.Row className="community-member-item" key={key}>
      <Table.Cell>
        <Grid textAlign="left" verticalAlign="middle">
          <Grid.Column width={4}>
            <Image src={avatar} avatar circular />
          </Grid.Column>
          <Grid.Column width={12}>
            <List>
              <List.Item as="a">{receiver.name || receiver.user}</List.Item>
              <List.Item as="small">{receiver.description}</List.Item>
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
                trigger={<Icon name="exclamation circle error" />}
              />
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Table.Cell>
      <Table.Cell>
        <RoleSelection
          canEditRole={randomBool()}
          initialValue={role.title}
          loading={isLoading}
          onChange={(role) => {
            onRoleChange(role);
          }}
          status={status}
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
  key: PropTypes.number.isRequired,
  onRoleChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  error: PropTypes.string,
  success: PropTypes.bool,
  onErrorClose: PropTypes.func,
  onSuccessTimeOut: PropTypes.func,
  onCancel: PropTypes.func.isRequired,
  onReInvite: PropTypes.func.isRequired,
  onView: PropTypes.func.isRequired,
};

InvitationResultItem.defaultProps = {
  isLoading: false,
  error: "",
  success: false,
  onErrorClose: () => null,
  onSuccessTimeOut: () => null,
};
