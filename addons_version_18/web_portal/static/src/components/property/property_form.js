/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class PropertyForm extends Component {
  static template = "web_portal.PropertyForm";

  setup() {
    const initial = this.props.initial || {};
    this.state = useState({
      formData: {
        name: initial.name || "",
        description: initial.description || "",
        postcode: initial.postcode || "",
        expected_price: initial.expected_price || "",
        bedrooms: initial.bedrooms || "",
        living_area: initial.living_area || "",
        facades: initial.facades || "",
        garage: initial.garage || false,
        garden: initial.garden || false,
        garden_area: initial.garden_area || "",
        garden_orientation: initial.garden_orientation || "north",
        expected_date_selling: initial.expected_date_selling || "",
      },
      errors: {},
      touched: {},
      isSubmitting: false,
      serverError: "",
    });
  }

  getValidationRules() {
    return {
      name: [
        { validate: (v) => v && v.trim() !== "", message: "Name is required." },
        {
          validate: (v) => !v || v.trim().length >= 3,
          message: "Name must be at least 3 characters.",
        },
        {
          validate: (v) => !v || v.trim().length <= 255,
          message: "Name cannot exceed 255 characters.",
        },
      ],
      postcode: [
        {
          validate: (v) => v && v.trim() !== "",
          message: "Postcode is required.",
        },
        {
          validate: (v) => !v || v.trim().length >= 3,
          message: "Postcode must be at least 3 characters.",
        },
        {
          validate: (v) => !v || v.trim().length <= 20,
          message: "Postcode cannot exceed 20 characters.",
        },
      ],
      expected_price: [
        {
          validate: (v) => !v || parseFloat(v) >= 0,
          message: "Expected price cannot be negative.",
        },
        {
          validate: (v) => !v || parseFloat(v) <= 99999999.99,
          message: "Expected price is too high.",
        },
      ],
      bedrooms: [
        {
          validate: (v) => !v || parseInt(v) >= 0,
          message: "Bedrooms cannot be negative.",
        },
        {
          validate: (v) => !v || parseInt(v) <= 100,
          message: "Bedrooms is unrealistic.",
        },
      ],
      living_area: [
        {
          validate: (v) => !v || parseInt(v) >= 0,
          message: "Living area cannot be negative.",
        },
        {
          validate: (v) => !v || parseInt(v) <= 100000,
          message: "Living area is unrealistic.",
        },
      ],
      facades: [
        {
          validate: (v) => !v || parseInt(v) >= 0,
          message: "Facades cannot be negative.",
        },
        {
          validate: (v) => !v || parseInt(v) <= 50,
          message: "Number of facades is unrealistic.",
        },
      ],
      garden_area: [
        {
          validate: (v) => !v || parseInt(v) >= 0,
          message: "Garden area cannot be negative.",
        },
        {
          validate: (v) => !v || parseInt(v) <= 100000,
          message: "Garden area is unrealistic.",
        },
      ],
      garden_orientation: [
        {
          validate: (v) => {
            const valid = [
              "north",
              "south",
              "east",
              "west",
              "northeast",
              "northwest",
              "southeast",
              "southwest",
            ];
            return valid.includes(v);
          },
          message: "Invalid garden orientation.",
        },
      ],
      description: [
        {
          validate: (v) => !v || v.length <= 2000,
          message: "Description cannot exceed 2000 characters.",
        },
      ],
      expected_date_selling: [
        {
          validate: (v) => {
            if (!v) return true;
            const d = new Date(v);
            return !isNaN(d.getTime());
          },
          message: "Invalid date format.",
        },
      ],
    };
  }

  validateField(name, value) {
    const rules = this.getValidationRules()[name] || [];
    for (const rule of rules) {
      if (!rule.validate(value)) return rule.message;
    }
    return null;
  }

  validateConditional(errors) {
    const next = { ...errors };
    if (this.state.formData.garden && !this.state.formData.garden_area) {
      next.garden_area = "Garden area is required when garden is selected.";
    } else if (
      !this.state.formData.garden &&
      next.garden_area === "Garden area is required when garden is selected."
    ) {
      delete next.garden_area;
    }
    return next;
  }

  validateAll() {
    const errors = {};
    const rules = this.getValidationRules();
    for (const fieldName of Object.keys(rules)) {
      const error = this.validateField(
        fieldName,
        this.state.formData[fieldName],
      );
      if (error) errors[fieldName] = error;
    }
    return this.validateConditional(errors);
  }

  onFieldChange(ev) {
    const { name, value, type, checked } = ev.target;
    const fieldValue = type === "checkbox" ? checked : value;
    this.state.formData[name] = fieldValue;

    if (this.state.touched[name]) {
      const error = this.validateField(name, fieldValue);
      if (error) this.state.errors[name] = error;
      else delete this.state.errors[name];
    }

    this.state.errors = this.validateConditional(this.state.errors);
  }

  onFieldBlur(ev) {
    const { name } = ev.target;
    this.state.touched[name] = true;
    const error = this.validateField(name, this.state.formData[name]);
    if (error) this.state.errors[name] = error;
    else delete this.state.errors[name];
    this.state.errors = this.validateConditional(this.state.errors);
  }

  async onSubmit(ev) {
    ev.preventDefault();
    this.state.serverError = "";

    const errors = this.validateAll();
    if (Object.keys(errors).length) {
      for (const fieldName of Object.keys(this.getValidationRules())) {
        this.state.touched[fieldName] = true;
      }
      this.state.errors = errors;
      return;
    }

    this.state.isSubmitting = true;
    ev.target.submit();
  }

  getFieldError(name) {
    return this.state.errors[name] || "";
  }

  shouldShowError(name) {
    return this.state.touched[name] && this.state.errors[name];
  }
}
