/** @odoo-module */

import { registry } from "@web/core/registry";
import { EmailField } from "@web/views/fields/email/email_field";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { _t } from "@web/core/l10n/translation";

class ValidEmailField extends EmailField {
  static template = "owl.ValidEmailField";
  static props = {
    ...standardFieldProps,
  };

  setup() {
    super.setup();
  }

  get isValidEmail() {
    const value = this.props.value;
    if (!value) return true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
  }

  get validationMessage() {
    return _t("Invalid Email Format");
  }

  update(value) {
    this.props.record.update({ [this.props.name]: value });
  }
}

registry.category("fields").add("valid_email", {
  component: ValidEmailField,
  supportedTypes: ["char"],
});
