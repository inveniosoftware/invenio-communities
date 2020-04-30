// This file is part of InvenioRDM
// Copyright (C) 2020 CERN.
// Copyright (C) 2020 Northwestern University.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from 'react';
import { Card } from 'semantic-ui-react';
import _truncate from 'lodash/truncate';

export function ResultsGridItemTemplate(record, index) {
    return (
      <Card fluid key={index} href={`/communities/${record.metadata.id}`}>
        <Card.Content>
          <Card.Header>{record.metadata.title}</Card.Header>
          <Card.Description>
          <div dangerouslySetInnerHTML={{ __html: record.metadata.description }} />
          </Card.Description>
        </Card.Content>
      </Card>
    );
}
