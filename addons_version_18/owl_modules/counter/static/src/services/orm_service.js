/** @odoo-module **/

import { registry } from "@web/core/registry";

export const ormService = {
    dependencies: ["rpc"],

    start(env, { rpc }) {
        console.log("✅ ORM Service started successfully!");

        return {
            async create(model, values) {
                console.log("🔵 ORM create:", model, values);
                return await rpc("/web/dataset/call_kw", {
                    model: model,
                    method: "create",
                    args: [values],
                    kwargs: {}
                });
            },

            async searchRead(model, domain = [], fields = [], limit = 80) {
                console.log("🔵 ORM searchRead:", model);
                return await rpc("/web/dataset/call_kw", {
                    model: model,
                    method: "search_read",
                    args: [],
                    kwargs: {
                        domain: domain,
                        fields: fields,
                        limit: limit,
                        order: "id desc"
                    }
                });
            },

            async write(model, ids, values) {
                return await rpc("/web/dataset/call_kw", {
                    model: model,
                    method: "write",
                    args: [ids, values],
                    kwargs: {}
                });
            },

            async unlink(model, ids) {
                return await rpc("/web/dataset/call_kw", {
                    model: model,
                    method: "unlink",
                    args: [ids],
                    kwargs: {}
                });
            }
        };
    }
};

try {
    registry.category("services").add("orm", ormService);
    console.log("✅ ORM Service registered!");
} catch (error) {
    console.log("⚠️ ORM Service already registered, skipping registration");
}