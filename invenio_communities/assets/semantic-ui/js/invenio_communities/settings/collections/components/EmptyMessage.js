// This file is part of Invenio-Communities
// Copyright (C) 2024-2025 CERN.
//
// Invenio-Communities is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Message } from "semantic-ui-react";

const EmptyMessage = ({ message }) => {
  return <Message icon="info" header={message} />;
};

EmptyMessage.propTypes = {
  message: PropTypes.string.isRequired,
};

export default EmptyMessage;
