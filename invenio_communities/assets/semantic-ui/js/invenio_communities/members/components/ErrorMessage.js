import React, { Component } from "react";
import PropTypes from "prop-types";
import { Message } from "semantic-ui-react";

export class ErrorMessage extends Component {
  render() {
    const { error } = this.props;
    return (
      <Message className="ml-20 mr-20" negative>
        <Message.Header>{error.message}</Message.Header>
        {error.errors && (
          <Message.List>
            {error.errors.map((error) => {
              return (
                <Message.Item>
                  <strong>{error.field}: </strong>
                  {error.messages.length === 1 ? (
                    error.messages[0]
                  ) : (
                    <Message.List>
                      {error.messages.map((message) => (
                        <Message.Item>{message}</Message.Item>
                      ))}
                    </Message.List>
                  )}
                </Message.Item>
              );
            })}
          </Message.List>
        )}
      </Message>
    );
  }
}

ErrorMessage.propTypes = {
  error: PropTypes.object.isRequired,
};
