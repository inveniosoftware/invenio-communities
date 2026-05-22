/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import { Card } from "semantic-ui-react";
import PropTypes from "prop-types";

export function MembersResultsGridItem({ result }) {
  return (
    <Card fluid href={`/members/${result.id}`}>
      <Card.Content>
        <Card.Header>{result.member.name}</Card.Header>
        <Card.Description>
          <div className="truncate-lines-1">{result.member.description}</div>
        </Card.Description>
      </Card.Content>
    </Card>
  );
}

MembersResultsGridItem.propTypes = {
  result: PropTypes.object.isRequired,
};
