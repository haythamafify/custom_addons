/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";

export class SmartCalculator extends Component {
    static template = "counter.SmartCalculator";
    static props = {
        onMounted: { type: Function, optional: true }
    };

    setup() {
        this.state = useState({
            number1: 0,
            number2: 0,
            result: 0
        });

        this.input1Ref = useRef("input1");

        // Call parent's onMounted with focus callback
        onMounted(() => {
            if (this.props.onMounted) {
                this.props.onMounted(() => this.focusFirstInput());
            }
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

    focusFirstInput() {
        if (this.input1Ref.el) {
            this.input1Ref.el.focus();
            this.input1Ref.el.select();
        }
    }
}