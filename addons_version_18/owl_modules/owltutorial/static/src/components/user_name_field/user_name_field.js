/** @odoo-module */

import { registry } from "@web/core/registry";
import { CharField } from "@web/views/fields/char/char_field";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

class UsernameField extends CharField {
  static template = "owl.UsernameField";
  static props = {
    ...standardFieldProps,
  };

  setup() {
    super.setup();
    console.log("Char Field Inherited");
    console.log(this.props);
  }

  get emailDomain() {
    const { email } = this.props.record.data;
    return email ? email.split("@")[1] : "";
  }

  update(value) {
    this.props.record.update({ [this.props.name]: value });
  }
}

registry.category("fields").add("username", {
  component: UsernameField,
  supportedTypes: ["char"],
});
