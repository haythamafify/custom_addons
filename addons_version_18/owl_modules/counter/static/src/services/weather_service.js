/** @odoo-module **/

import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";

export const weatherService = {
    dependencies: [],

    start() {
        const state = reactive({
            city: "Cairo",
            temperature: 25,
            condition: "Sunny",
            humidity: 60,
            isLoading: false
        });

        return {
            get city() {
                return state.city;
            },

            get temperature() {
                return state.temperature;
            },

            get condition() {
                return state.condition;
            },

            get humidity() {
                return state.humidity;
            },

            get isLoading() {
                return state.isLoading;
            },

            async fetchWeather(cityName) {
                state.isLoading = true;

                try {
                    // Simulate API call
                    await new Promise(resolve => setTimeout(resolve, 1000));

                    // Mock weather data
                    const weatherData = this._getMockWeatherData(cityName);

                    state.city = cityName;
                    state.temperature = weatherData.temperature;
                    state.condition = weatherData.condition;
                    state.humidity = weatherData.humidity;

                } catch (error) {
                    console.error("Error fetching weather:", error);
                } finally {
                    state.isLoading = false;
                }
            },

            _getMockWeatherData(city) {
                const mockData = {
                    "Cairo": { temperature: 28, condition: "Sunny", humidity: 55 },
                    "Alexandria": { temperature: 26, condition: "Partly Cloudy", humidity: 70 },
                    "London": { temperature: 15, condition: "Rainy", humidity: 85 },
                    "New York": { temperature: 22, condition: "Cloudy", humidity: 65 },
                    "Dubai": { temperature: 35, condition: "Hot", humidity: 45 }
                };

                return mockData[city] || {
                    temperature: 20,
                    condition: "Clear",
                    humidity: 60
                };
            },

            updateCity(newCity) {
                state.city = newCity;
            }
        };
    }
};

registry.category("services").add("weather", weatherService);