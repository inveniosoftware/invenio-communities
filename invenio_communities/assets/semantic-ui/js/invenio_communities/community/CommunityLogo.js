/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { Image } from "react-invenio-forms";
import PropTypes from "prop-types";

/** Community logo, or the backend's placeholder from the UI serialization (`ui.logo_url`). */
export const CommunityLogo = ({ community, ...imageProps }) => {
  const src = community.ui?.logo_url ?? community.links.logo;
  if (!src) {
    return null;
  }
  return <Image src={src} alt="" {...imageProps} />;
};

CommunityLogo.propTypes = {
  community: PropTypes.object.isRequired,
};
