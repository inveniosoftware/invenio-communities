// This file is part of InvenioRDM
// Copyright (C) 2024 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Popup } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

const OrganizationsList = ({ organizations }) => {
  const handleClick = (e) => {
    e.preventDefault();
  };

  return (
    <div>
      {organizations && organizations.length > 0 && (
        <div>
          <span className="org-list-inline">
            <i className="building outline icon" aria-hidden="true" />
            {organizations[0].id ? (
              <a
                href={organizations[0].url}
                aria-label={`${organizations[0].name}'s ${organizations[0].label} profile`}
                title={`${organizations[0].name}'s ${organizations[0].label} profile`}
                target="_blank"
                rel="noreferrer"
              >
                {organizations[0].name}
                <span>&nbsp;</span>
                <img
                  className="inline-id-icon"
                  src={organizations[0].icon}
                  alt={`${organizations[0].name}'s ${organizations[0].label} profile`}
                />
              </a>
            ) : (
              organizations[0].name
            )}
          </span>
          {organizations.length > 1 && (
            <span className="ml-1">
              &nbsp;{i18next.t("and")}&nbsp;
              <Popup
                trigger={
                  <a href="#!" onClick={handleClick}>
                    {i18next.t("{{count}} more organizations", {
                      count: organizations.length - 1,
                    })}
                  </a>
                }
                size="small"
                wide="very"
                content={
                  <div className="expanded-orgs">
                    {organizations.slice(1).map((org, index) => (
                      <div key={org.id || org.name} className="inline-computer mt-5">
                        {org.id ? (
                          <a
                            href={org.url}
                            aria-label={`${org.name}'s ${org.label} profile`}
                            title={`${org.name}'s ${org.label} profile`}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {org.name}
                            <span>&nbsp;</span>
                            <img
                              className="inline-id-icon"
                              src={org.icon}
                              alt={`${org.name}'s ${org.label} profile`}
                            />
                          </a>
                        ) : (
                          org.name
                        )}
                        {index < organizations.length - 2 && <span>{", "}&nbsp;</span>}
                      </div>
                    ))}
                  </div>
                }
                on="click"
                position="bottom left"
                positionFixed
              />
            </span>
          )}
        </div>
      )}
    </div>
  );
};

OrganizationsList.propTypes = {
  organizations: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string.isRequired,
      label: PropTypes.string,
      icon: PropTypes.string,
      url: PropTypes.string,
    })
  ).isRequired,
};

export default OrganizationsList;
