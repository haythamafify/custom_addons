/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

import { Component, useState, onWillUpdateProps } from "@odoo/owl";

export class RangeField extends Component {
  static template = "owl.RangeField";
  static props = {
    ...standardFieldProps,
  };

  setup() {
    this.state = useState({
      range: String(this.props.value || 100),
    });

    onWillUpdateProps((newProps) => {
      this.state.range = String(newProps.value || 100);
    });

    const { currency_id } = this.props.record.data;
    this.currency = currency_id ? currency_id[1] : "";
  }

  update(value) {
    const intValue = parseInt(value) || 0;
    this.props.record.update({ [this.props.name]: intValue });
  }
}

registry.category("fields").add("range", {
  component: RangeField,
  supportedTypes: ["integer"],
});
