/** @odoo-module **/

import { Component, useSubEnv } from "@odoo/owl"; // Add useSubEnv import here
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";

export class OdooDashboard extends Component {
  static template = "owl.OdooDashboardTemplate";
  static components = { Layout };

  setup() {
    useSubEnv({ config: this.env.config });
  }

  get getowl_basicService() {
    console.log("getowl_basicService");
    const basicService = this.env.services.basicService;
    return basicService || {};
  }

  stringifyObject(obj) {
    return JSON.stringify(obj);
  }
}

registry.category("actions").add("owl.odoo_dashboard", OdooDashboard);
