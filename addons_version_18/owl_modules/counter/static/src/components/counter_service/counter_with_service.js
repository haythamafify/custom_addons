/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CounterWithService extends Component {
    static template = "counter.CounterWithService";

    setup() {
        this.counterService = useService("counter");
    }

    get counterValue() {
        return this.counterService.value;
    }

    onIncrement() {
        this.counterService.increment();
    }

    onDecrement() {
        this.counterService.decrement();
    }

    onReset() {
        this.counterService.reset();
    }
}

registry.category("actions").add("counter_service.action", CounterWithService);