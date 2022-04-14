import { i18next } from "@translations/invenio_communities/i18next";

export const memberVisibilityTypes = [
  {
    name: "public",
    visible: true,
    title: i18next.t("Public"),
    description: i18next.t(
      "Member publicly visible in the community members list"
    ),
  },
  {
    name: "hidden",
    visible: false,
    title: i18next.t("Hidden"),
    description: i18next.t("Member hidden in the community members list"),
  },
];
