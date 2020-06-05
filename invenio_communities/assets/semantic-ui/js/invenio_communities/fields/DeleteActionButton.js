import React from 'react';
import PropTypes from 'prop-types';
import { ActionButton } from "react-invenio-forms";

export class DeleteActionButton extends React.Component {
  render() {
    const { deleteClick, ...uiProps} = this.props;
    return (
      <ActionButton
      // TODO: use `isDisabled`
      isDisabled={() => false}
      name=""
      onClick={this.deleteClick}
      negative
      {...uiProps}
    >
    </ActionButton>
    );
  }
}

