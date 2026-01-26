/** @odoo-module */

import { registry } from "@web/core/registry";
import { EmailField } from "@web/views/fields/email/email_field";
import { _t } from "@web/core/l10n/translation";

class ValidEmailField extends EmailField {
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

ValidEmailField.template = "owl.ValidEmailField";

registry.category("fields").add("valid_email", {
  component: ValidEmailField,
  supportedTypes: ["char"],
});
