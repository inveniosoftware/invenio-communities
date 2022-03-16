/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import { randomKey, roles, randomBool } from "../mock";
import { DateTime } from "luxon";
import {
  Table,
  Grid,
  Container,
  List,
  Dropdown,
  Icon,
  Loader,
} from "semantic-ui-react";
import { Image } from "react-invenio-forms";
import { ActionButtons } from "./InvitationActionButtons";
import PropTypes from "prop-types";
import { ErrorPopup } from "../components/ErrorPopup";
import { i18next } from "@translations/invenio_communities/i18next";

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

const RoleSelection = ({ currentValue, onChange }) => {
  const options = roles.map(({ title, description }, index) => ({
    key: randomKey(index),
    text: title,
    value: title.toLowerCase(),
    is_selected: currentValue === title,
    content: <RoleContent title={title} description={description} />,
  }));

  return (
    <Dropdown
      selection
      options={options}
      value={currentValue}
      onChange={onChange}
    />
  );
};

export class InvitationResultItem extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    const {
      invitation,
      onRoleChange,
      isLoading,
      key,
      error,
      success,
      currentRole,
      onErrorClose,
    } = this.props;
    const { receiver, status, expires_at } = invitation;

    const formattedTime = DateTime.fromISO(expires_at)
      .setLocale(i18next.language)
      .toRelative();

    return (
      <Table.Row className="community-member-item" key={key}>
        <Table.Cell>
          <Grid textAlign="left" verticalAlign="middle">
            <Grid.Column width={4}>
              <Image
                src={receiver.links.avatar}
                fallbackSrc="/static/images/square-placeholder.png"
                avatar
                circular
              />
            </Grid.Column>
            <Grid.Column width={12}>
              <List>
                <List.Item as="a">{receiver.name}</List.Item>
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
                {formattedTime}
              </Grid.Column>
              <Grid.Column width={3} textAlign="right">
                {isLoading && <Loader active inline="centered" size="small" />}
                {success && <Icon color="green" name="checkmark" />}
                {error && (
                  <ErrorPopup
                    onClose={onErrorClose}
                    error={error}
                    trigger={
                      <Icon
                        name="exclamation circle"
                        className="error-colored"
                      />
                    }
                  />
                )}
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Table.Cell>
        <Table.Cell>
          <RoleSelection
            canEditRole={randomBool()}
            currentValue={currentRole}
            loading={isLoading}
            onChange={(e, { value: role }) => {
              onRoleChange(role);
            }}
          />
        </Table.Cell>
        <Table.Cell>
          <Container fluid textAlign="right">
            <ActionButtons status={status} />
          </Container>
        </Table.Cell>
      </Table.Row>
    );
  }
}

InvitationResultItem.propTypes = {
  invitation: PropTypes.object.isRequired,
  key: PropTypes.number.isRequired,
  onRoleChange: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  error: PropTypes.string,
  success: PropTypes.bool,
  currentRole: PropTypes.string.isRequired,
  onErrorClose: PropTypes.func,
};

InvitationResultItem.defaultProps = {
  isLoading: false,
  error: "",
  success: false,
  onErrorClose: () => null,
};
