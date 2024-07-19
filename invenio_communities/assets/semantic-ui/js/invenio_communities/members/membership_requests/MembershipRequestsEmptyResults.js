import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Header, Icon, Segment } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";

class MembershipRequestsEmptyResultsCmp extends Component {
  render() {
    const { resetQuery, extraContent, queryString } = this.props;

    return (
      <Segment.Group>
        <Segment placeholder textAlign="center">
          <Header icon>
            <Icon name="search" />
            {i18next.t("No matching members found.")}
          </Header>
          {queryString && (
            <p>
              <em>
                {i18next.t("Current search")} "{queryString}"
              </em>
            </p>
          )}
          <Button primary onClick={() => resetQuery()}>
            {i18next.t("Clear query")}
          </Button>
          {extraContent}
        </Segment>
      </Segment.Group>
    );
  }
}

MembershipRequestsEmptyResultsCmp.propTypes = {
  resetQuery: PropTypes.func.isRequired,
  queryString: PropTypes.string.isRequired,
  extraContent: PropTypes.node,
};

MembershipRequestsEmptyResultsCmp.defaultProps = {
  extraContent: null,
};

export const MembershipRequestsEmptyResults = withState(
  MembershipRequestsEmptyResultsCmp
);
