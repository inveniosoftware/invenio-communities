/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Segment, Label, Icon, Header } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { Image } from "react-invenio-forms";
import _isEmpty from "lodash/isEmpty";

export class SelectedMembers extends Component {
  removeMember = (id) => {
    const { selectedMembers, updateSelectedMembers } = this.props;
    const newSelectedMembers = selectedMembers.filter(
      (element) => element.id != id
    );
    updateSelectedMembers(newSelectedMembers);
  };

  render() {
    const { selectedMembers } = this.props;
    return !_isEmpty(selectedMembers) ? (
      <>
        <Header as="h4" className="ml-20">
          {i18next.t("Selected members and groups:")}
        </Header>
        <Segment className="selected-members-header mb-20 mr-20 ml-20">
          {selectedMembers.map((element, index) => (
            <Label className="mb-5 ml-5" image>
              <Image src={element.avatar} />
              {element.name}
              <Icon
                onClick={() => this.removeMember(element.id)}
                name="delete"
              />
            </Label>
          ))}
        </Segment>
      </>
    ) : (
      <div className="selected-members-header mb-20">
        <Segment className="mr-20 ml-20 empty-members" placeholder>
          <Header icon>
            <Icon name="users" />
            {i18next.t("No people or groups selected.")}
          </Header>
        </Segment>
      </div>
    );
  }
}

SelectedMembers.propTypes = {
  selectedMembers: PropTypes.array.isRequired,
  updateSelectedMembers: PropTypes.func.isRequired,
};
