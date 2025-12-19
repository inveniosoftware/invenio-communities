import { i18next } from "@translations/invenio_rdm_records/i18next";

import React, { Component } from "react";

import { Menu } from "semantic-ui-react";
import PropTypes from "prop-types";

export class CommunitiesStatusFilter extends Component {
  render() {
    const {
      myCommunitiesOnClick,
      allCommunitiesOnClick,
      appID,
      allCommunitiesSelected,
    } = this.props;

    return (
      <Menu role="tablist" className="theme-primary-menu" compact>
        <Menu.Item
          as="button"
          role="tab"
          id="all-communities-tab"
          aria-selected={allCommunitiesSelected}
          aria-controls={appID}
          name="All"
          active={allCommunitiesSelected}
          onClick={allCommunitiesOnClick}
        >
          {i18next.t("All")}
        </Menu.Item>
        <Menu.Item
          as="button"
          role="tab"
          id="my-communities-tab"
          aria-selected={!allCommunitiesSelected}
          aria-controls={appID}
          name="My communities"
          active={!allCommunitiesSelected}
          onClick={myCommunitiesOnClick}
        >
          {i18next.t("My communities")}
        </Menu.Item>
      </Menu>
    );
  }
}

CommunitiesStatusFilter.propTypes = {
  allCommunitiesOnClick: PropTypes.func.isRequired,
  myCommunitiesOnClick: PropTypes.func.isRequired,
  allCommunitiesSelected: PropTypes.bool,
  appID: PropTypes.string.isRequired,
};

CommunitiesStatusFilter.defaultProps = {
  allCommunitiesSelected: true,
};
