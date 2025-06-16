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
    const [filterType, filterValue] = filter;
    let filterData;

    switch (filterType) {
      case "role":
        filterData = this.getRoles()[filterType];
        break;
      case "visibility":
        filterData = this.getVisibility()[filterType];
        break;
      case "status":
        filterData = this.getStatus()[filterType];
        break;
      default:
        filterData = null;
        break;
    }

    const matchingBucket = filterData?.buckets?.find(
      (bucket) => bucket.key === filterValue
    );

    const label = filterData?.label ?? _upperFirst(filterType);

    const value = matchingBucket?.label ?? _upperFirst(filterValue);

    return `${label}: ${value}`;
  }
}
