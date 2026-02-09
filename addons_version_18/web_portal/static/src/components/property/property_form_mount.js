/** @odoo-module **/

import { mount, whenReady } from "@odoo/owl";
import { PropertyForm } from "./property_form";

function getInputValue(formEl, name) {
  const input = formEl.querySelector(`[name="${name}"]`);
  if (!input) return "";
  if (input.type === "checkbox") return input.checked;
  return input.value || "";
}

whenReady(() => {
  const formEl = document.querySelector("form.property-form");
  if (!formEl) return;

  const initial = {
    name: getInputValue(formEl, "name"),
    description: getInputValue(formEl, "description"),
    postcode: getInputValue(formEl, "postcode"),
    expected_price: getInputValue(formEl, "expected_price"),
    bedrooms: getInputValue(formEl, "bedrooms"),
    living_area: getInputValue(formEl, "living_area"),
    facades: getInputValue(formEl, "facades"),
    garage: getInputValue(formEl, "garage"),
    garden: getInputValue(formEl, "garden"),
    garden_area: getInputValue(formEl, "garden_area"),
    garden_orientation: getInputValue(formEl, "garden_orientation"),
    expected_date_selling: getInputValue(formEl, "expected_date_selling"),
  };

  const action = formEl.getAttribute("action") || "";
  const csrfToken = getInputValue(formEl, "csrf_token");
  const isEdit = action.includes("/edit");

  const root = document.createElement("div");
  formEl.replaceWith(root);

  mount(PropertyForm, {
    target: root,
    props: { initial, action, csrfToken, isEdit },
  });
});
