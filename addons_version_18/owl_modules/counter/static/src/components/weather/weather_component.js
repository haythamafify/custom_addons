/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class WeatherComponent extends Component {
    static template = "counter.WeatherComponent";

    setup() {
        this.weatherService = useService("weather");
        this.state = useState({
            searchCity: ""
        });

        this.cities = ["Cairo", "Alexandria", "London", "New York", "Dubai"];
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

    async onCityClick(city) {
        await this.weatherService.fetchWeather(city);
    }

    async onSearchCity() {
        if (this.state.searchCity.trim()) {
            await this.weatherService.fetchWeather(this.state.searchCity);
            this.state.searchCity = "";
        }
    }

    onInputChange(ev) {
        this.state.searchCity = ev.target.value;
    }
}

registry.category("actions").add("weather.action", WeatherComponent);