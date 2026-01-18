/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class IntegratedWorkspace extends Component {
    static template = "counter.IntegratedWorkspace";

    setup() {
        this.counterService = useService("counter");
        this.weatherService = useService("weather");
    }

    get counterValue() {
        return this.counterService.value;
    }

    get currentCity() {
        return this.weatherService.city;
    }

    get temperature() {
        return this.weatherService.temperature;
    }

    get condition() {
        return this.weatherService.condition;
    }

    get humidity() {
        return this.weatherService.humidity;
    }

    get isLoading() {
        return this.weatherService.isLoading;
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

    async onCityChange(ev) {
        const city = ev.target.value;
        if (city) {
            await this.weatherService.fetchWeather(city);
        }
    }
}

registry.category("actions").add("integrated_workspace.action", IntegratedWorkspace);