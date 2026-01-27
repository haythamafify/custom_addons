/** @odoo-module */

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useState, onWillUpdateProps } from "@odoo/owl";

class UsernameField extends CharField {
  static template = "owl.UsernameField";
  static props = {
    ...standardFieldProps,
  };

  setup() {
    super.setup();

    this.state = useState({
      username: this.props.value || "",
    });

    onWillUpdateProps((newProps) => {
      this.state.username = newProps.value || "";
    });
  }

  get emailDomain() {
    const { email } = this.props.record.data;
    return email ? email.split("@")[1] : "";
  }

  update(value) {
    this.state.username = value;
    this.props.record.update({ [this.props.name]: value });
  }
}

registry.category("fields").add("username", {
  component: UsernameField,
  supportedTypes: ["char"],
});
