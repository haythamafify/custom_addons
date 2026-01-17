/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Counter extends Component {
    static template = "counter.Counter";
    
    setup() {
        this.state = useState({ counter: 0 });
    }
    
    increment() {
        this.state.counter++;
    }
    
    decrement() {
        this.state.counter--;
    }
    
    reset() {
        this.state.counter = 0;
    }
}

registry.category("actions").add("counter.action", Counter);