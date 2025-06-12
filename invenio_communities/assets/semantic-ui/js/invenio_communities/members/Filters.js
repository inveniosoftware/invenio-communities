import _upperFirst from "lodash/upperFirst";
import { i18next } from "@translations/invenio_communities/i18next";

export class Filters {
  constructor(configRoles) {
    this.configRoles = configRoles;
  }
  /*
   * Serializes a filter to be processed by ES
   * @param {String} type Name of the filter type in ES
   * @param {String} labelName Name of the label to be displayed
   * @param {Array.<{key: String, label: String}>} values The values as ES produce them
   */
  serializeFilter(type, labelName, values) {
    return { [type]: { buckets: values, label: labelName } };
  }

  getRoles() {
    const values = [];
    this.configRoles?.forEach((role) => {
      values.push({ key: role.name, label: role.title });
    });
    return this.serializeFilter("role", i18next.t("Role"), values);
  }

  getVisibility() {
    const values = [
      { key: "true", label: i18next.t("Public") },
      { key: "false", label: i18next.t("Hidden") },
    ];
    return this.serializeFilter("visibility", i18next.t("Visibility"), values);
  }

  getStatus() {
    // This are the values that allow to filter for archived invitations
    const values = [
      { key: "submitted", label: i18next.t("Submitted") },
      { key: "accepted", label: i18next.t("Accepted") },
      { key: "declined", label: i18next.t("Declined") },
      { key: "cancelled", label: i18next.t("Cancelled") },
      { key: "expired", label: i18next.t("Expired") },
    ];
    return this.serializeFilter("status", i18next.t("Status"), values);
  }

  getInvitationFilters() {
    const statusFilters = this.getStatus();
    const rolesFilters = this.getRoles();
    return { ...rolesFilters, ...statusFilters };
  }

  getMembersFilters() {
    const visibilityFilters = this.getVisibility();
    const rolesFilters = this.getRoles();
    return { ...rolesFilters, ...visibilityFilters };
  }

  getHumanReadableVisibility(value) {
    return value === "true" ? i18next.t("Public") : i18next.t("Hidden");
  }

  getDisplayValue(filter) {
    let filterInformation;
    switch (filter[0]) {
      case "role":
        filterInformation = this.getRoles()[filter[0]];
        break;
      case "visibility":
        filterInformation = this.getVisibility()[filter[0]];
        break;
      case "status":
        filterInformation = this.getStatus()[filter[0]];
        break;
      default:
        filterInformation = null;
    }
    // use localized values if available, otherwise fallback to previous behavior
    const filterLabel = filterInformation?.label || filter[0];
    const filterValue =
      filterInformation?.buckets?.find((bucket) => bucket.key === filter[1])?.label ||
      _upperFirst(filter[1]);
    return `${filterLabel}: ${filterValue}`;
  }
}
