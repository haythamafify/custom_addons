/** @odoo-module **/

import { registry } from "@web/core/registry";

export const owldashboardsService = {
  dashBoard_data: {},
  start() {
    console.log("Owl Dashboards Service started");
  },
};

registry.category("services").add("owldashboardsService", owldashboardsService);
