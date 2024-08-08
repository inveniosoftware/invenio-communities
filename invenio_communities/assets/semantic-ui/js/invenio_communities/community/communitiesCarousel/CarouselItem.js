/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import _truncate from "lodash/truncate";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image, InvenioPopup } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Button, Grid, Header, Item, Icon } from "semantic-ui-react";

class CarouselItem extends Component {
  render() {
    const { community, defaultLogo, className, showUploadBtn, canSubmitRecord } =
      this.props;
    return (
      <Overridable
        id="InvenioCommunities.CarouselItem.layout"
        community={community}
        defaultLogo={defaultLogo}
        className={className}
      >
        <Item
          className={`carousel flex align-items-center ${className}`}
          key={community.id}
        >
          <Image size="small" src={community.links.logo} fallbackSrc={defaultLogo} />
          <Item.Content>
            <Item.Header as={Grid} stackable className="rel-pb-1">
              <Grid.Column computer="10" tablet="16" className="pl-0 pb-0">
                <Header as="a" size="medium" href={community.links.self_html}>
                  {community.metadata.title}
                </Header>
              </Grid.Column>
              <Grid.Column computer="6" tablet="16" className="buttons pl-0 pb-0">
                <Button
                  size="mini"
                  href={community.links.self_html}
                  content={i18next.t("Browse")}
                />
                {showUploadBtn && (
                  <>
                    <Button
                      size="mini"
                      icon="upload"
                      labelPosition="left"
                      positive
                      href={`/uploads/new?community=${community.slug}`}
                      content={i18next.t("New upload")}
                      disabled={!canSubmitRecord}
                    />
                    {!canSubmitRecord && (
                      <InvenioPopup
                        popupId="community-inclusion-info-popup"
                        size="small"
                        trigger={
                          <Icon
                            className="mb-5"
                            color="grey"
                            name="question circle outline"
                          />
                        }
                        ariaLabel={i18next.t(
                          "Submission to this community is only allowed to community members."
                        )}
                        content={i18next.t(
                          "Submission to this community is only allowed to community members."
                        )}
                      />
                    )}
                  </>
                )}
              </Grid.Column>
            </Item.Header>
            <Item.Description
              content={_truncate(community.metadata.description, { length: 300 })}
            />
          </Item.Content>
        </Item>
      </Overridable>
    );
  }
}

CarouselItem.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  className: PropTypes.string,
  showUploadBtn: PropTypes.bool,
  canSubmitRecord: PropTypes.bool.isRequired,
};

CarouselItem.defaultProps = {
  className: "",
  showUploadBtn: true,
};

export default Overridable.component("InvenioCommunities.CarouselItem", CarouselItem);
