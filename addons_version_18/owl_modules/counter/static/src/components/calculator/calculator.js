/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Calculator extends Component {
    static template = "calculator.Calculator";

    setup() {
        this.state = useState({
            number1: 0,
            number2: 0,
            result: 0
        });
    }

    onNumber1Change(ev) {
        this.state.number1 = parseFloat(ev.target.value) || 0;
        this.calculateResult();
    }

    onNumber2Change(ev) {
        this.state.number2 = parseFloat(ev.target.value) || 0;
        this.calculateResult();
    }

    calculateResult() {
        this.state.result = this.state.number1 + this.state.number2;
    }

    reset() {
        this.state.number1 = 0;
        this.state.number2 = 0;
        this.state.result = 0;
    }
}

registry.category("actions").add("calculator.action", Calculator);