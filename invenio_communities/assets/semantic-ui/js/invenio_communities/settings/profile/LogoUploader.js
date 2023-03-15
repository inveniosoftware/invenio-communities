/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 * Copyright (C) 2021-2022 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import React from "react";
import Dropzone from "react-dropzone";
import { humanReadableBytes } from "react-invenio-deposit";
import { Image } from "react-invenio-forms";
import { Button, Divider, Header, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { DeleteButton } from "./DeleteButton";
import PropTypes from "prop-types";

/**
 * Remove empty fields from community
 * Copied from react-invenio-deposit
 * @method
 * @param {object} obj - potentially empty object
 * @returns {object} community - without empty fields
 */

const LogoUploader = ({ community, defaultLogo, hasLogo, onError, logoMaxSize }) => {
  const currentUrl = new URL(window.location.href);
  let dropzoneParams = {
    preventDropOnDocument: true,
    onDropAccepted: async (acceptedFiles) => {
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append("file", file);

      try {
        const client = new CommunityApi();
        await client.updateLogo(community.id, file);
        // set param that logo was updated
        currentUrl.searchParams.set("updated", "true");

        window.location.replace(currentUrl.href);
      } catch (error) {
        onError(error);
      }
    },
    onDropRejected: (rejectedFiles) => {
      // TODO: show error message when files are rejected e.g size limit
      console.error(rejectedFiles[0].errors);
    },
    multiple: false,
    noClick: true,
    noDrag: true,
    noKeyboard: true,
    disabled: false,
    maxFiles: 1,
    maxSize: 5000000, // 5Mb limit
    accept: ".jpeg,.jpg,.png",
  };

  const deleteLogo = async () => {
    const client = new CommunityApi();
    await client.deleteLogo(community.id);
  };

  // when uploading a new logo, the previously cached logo will be displayed instead of the new one. Avoid it by randomizing the URL.
  const logoURL = new URL(community.links.logo);
  const noCacheRandomValue = new Date().getMilliseconds() * 5;
  logoURL.searchParams.set("no-cache", noCacheRandomValue.toString());

  const logoWasUpdated = currentUrl.searchParams.has("updated");

  return (
    <Dropzone {...dropzoneParams}>
      {({ getRootProps, getInputProps, open: openFileDialog }) => (
        <>
          <span {...getRootProps()}>
            <input {...getInputProps()} />
            <Header className="mt-0">{i18next.t("Profile picture")}</Header>
            <Image
              src={logoURL}
              fallbackSrc={defaultLogo}
              loadFallbackFirst
              fluid
              wrapped
              rounded
              className="community-logo settings"
            />

            <Divider hidden />
          </span>

          <Button
            fluid
            icon
            labelPosition="left"
            type="button"
            onClick={openFileDialog}
            className="rel-mt-1 rel-mb-1"
          >
            <Icon name="upload" />
            {i18next.t("Upload new picture")}
          </Button>
          <label className="helptext">
            {i18next.t("File must be smaller than ")}
            {humanReadableBytes(logoMaxSize, true)}
          </label>
          {hasLogo && (
            <DeleteButton
              label={i18next.t("Delete picture")}
              redirectURL={`${community.links.self_html}/settings?updated=true`}
              confirmationMessage={
                <Header as="h2" size="medium">
                  {i18next.t("Are you sure you want to delete this picture?")}
                </Header>
              }
              onDelete={deleteLogo}
              onError={onError}
            />
          )}
          {logoWasUpdated && (
            <Message
              info
              icon="warning circle"
              size="small"
              content={i18next.t(
                "It may take a few moments for changes to be visible everywhere"
              )}
            />
          )}
        </>
      )}
    </Dropzone>
  );
};

LogoUploader.propTypes = {
  community: PropTypes.object.isRequired,
  defaultLogo: PropTypes.string.isRequired,
  hasLogo: PropTypes.bool.isRequired,
  onError: PropTypes.func.isRequired,
  logoMaxSize: PropTypes.number.isRequired,
};

export default LogoUploader;
