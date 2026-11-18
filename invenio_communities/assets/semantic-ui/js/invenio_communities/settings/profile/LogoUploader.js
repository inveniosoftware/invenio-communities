/*
 * SPDX-FileCopyrightText: 2016-2022 CERN.
 * SPDX-FileCopyrightText: 2021-2023 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { useState } from "react";
import Dropzone from "react-dropzone";
import { http, humanReadableBytes } from "react-invenio-forms";
import { Button, Divider, Header, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { CommunityLogo } from "../../community/CommunityLogo";
import { DeleteButton } from "./DeleteButton";
import PropTypes from "prop-types";

const LogoUploader = ({ community, onError, logoMaxSize }) => {
  /* State */
  // props initilization is fine since original props don't change after
  // initial mounting.
  const [logoCommunity, setLogoCommunity] = useState(community);
  const [logoUpdated, logoSetUpdated] = useState(false);

  // Refetch so the logo URL (versioned, or the placeholder) comes from the backend
  const refreshLogo = async () => {
    const response = await http.get(community.links.self);
    setLogoCommunity(response.data);
    logoSetUpdated(true);
  };

  let dropzoneParams = {
    preventDropOnDocument: true,
    onDropAccepted: async (acceptedFiles) => {
      const file = acceptedFiles[0];

      try {
        const client = new CommunityApi();
        await client.updateLogo(community.id, file);
        await refreshLogo();
        onError({ response: { data: { message: "", errors: null, status: null } } });
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
    await refreshLogo();
  };

  return (
    <Dropzone {...dropzoneParams}>
      {({ getRootProps, getInputProps, open: openFileDialog }) => (
        <>
          <span {...getRootProps()}>
            <input {...getInputProps()} />
            <Header as="h2" size="small" className="mt-0">
              {i18next.t("Profile picture")}
            </Header>
            <CommunityLogo
              /* Change in key will cause a remounting. */
              key={logoCommunity.ui?.logo_url}
              community={logoCommunity}
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
            {i18next.t("File must be smaller than {{fileSize}}", {
              fileSize: humanReadableBytes(logoMaxSize, true),
            })}
          </label>
          {logoCommunity.logo && (
            <DeleteButton
              id="delete-picture-button"
              label={i18next.t("Delete picture")}
              confirmationMessage={
                <Header as="h2" size="medium">
                  {i18next.t("Are you sure you want to delete this picture?")}
                </Header>
              }
              onDelete={deleteLogo}
              onError={onError}
            />
          )}
          {logoUpdated && (
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
  onError: PropTypes.func.isRequired,
  logoMaxSize: PropTypes.number.isRequired,
};

export default LogoUploader;
