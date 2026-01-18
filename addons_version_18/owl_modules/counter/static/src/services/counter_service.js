/** @odoo-module **/

import { reactive } from "@odoo/owl";

export const counterService = {
    dependencies: [],

    start() {
        const state = reactive({
            value: 0
        });

        return {
            get value() {
                return state.value;
            },

            increment() {
                state.value++;
            },

            decrement() {
                state.value--;
            },

            reset() {
                state.value = 0;
            },

            setValue(newValue) {
                if (typeof newValue === 'number') {
                    state.value = newValue;
                }
            }
        };
    }
};

import { registry } from "@web/core/registry";
registry.category("services").add("counter", counterService);