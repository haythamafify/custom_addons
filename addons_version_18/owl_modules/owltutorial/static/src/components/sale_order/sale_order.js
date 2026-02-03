/** @odoo-module **/
import { FormController } from "@web/views/form/form_controller";
import { formView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { useEffect } from "@odoo/owl";

export class CustomSaleFormController extends FormController {
  disableForm() {
    const root = this.model?.root;

    if (!root) {
      return;
    }

    if (typeof root.switchMode === "function") {
      root.switchMode("readonly");
      return;
    }

    if (typeof root.update === "function") {
      root.update({ mode: "readonly" });
      return;
    }

    if (typeof this.model?.setMode === "function") {
      this.model.setMode("readonly");
    }
  }

  setup() {
    super.setup();
    console.log("CustomSaleFormController Ready!");

  
    useEffect(() => {
      this.disableForm();
    }, () => [this.model?.root]);
  }


}

const sale_order_form_view = {
  ...formView,
  type: "form",
  Controller: CustomSaleFormController,
};

// Register the view
registry.category("views").add("sale_order_form_disable", sale_order_form_view);
