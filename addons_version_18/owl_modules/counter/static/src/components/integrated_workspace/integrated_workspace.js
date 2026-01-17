/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { SmartCounter } from "../smart_counter/smart_counter";
import { SmartCalculator } from "../smart_calculator/smart_calculator";

export class IntegratedWorkspace extends Component {
    static template = "counter.IntegratedWorkspace";
    static components = { SmartCounter, SmartCalculator };

    setup() {
        this.calculatorFocusCallback = null;
    }

    onCalculatorMounted(focusCallback) {
        // Save the callback when calculator is mounted
        this.calculatorFocusCallback = focusCallback;
    }

    onTimeExceeded() {
        // Call the focus callback
        if (this.calculatorFocusCallback) {
            this.calculatorFocusCallback();

            // Show notification
            this.env.services.notification.add(
                "⚠️ Time limit exceeded! Please use the calculator to verify your work.",
                { type: "warning", sticky: false }
            );
        }
    }
}

registry.category("actions").add("integrated_workspace.action", IntegratedWorkspace);