/** @odoo-module **/

import { markup } from "@odoo/owl";
import { registry } from "@web/core/registry";

function stringifyObject(obj) {
  return JSON.stringify(obj, null, 2);
}

export const basicService = {
  start() {
    return {
      string: "Basic Service",
      boolean: true,
      integer: 1,
      float: 0.5,
      array: [1, 2, 3],
      object: { key: "value" },
      function: () => {
        console.log("This function has been called");
        return "Service function has been called.";
      },
      normal_function: () => "This is a normal function",
      arrow_function: () => "This is an arrow function",
      html: markup(`<button class="btn btn-sm btn-primary">HTML Button</button>`),
    };
  },
};

registry.category("services").add("basicService", basicService);
