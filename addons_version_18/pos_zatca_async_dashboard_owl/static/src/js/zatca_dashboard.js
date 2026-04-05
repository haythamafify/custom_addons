/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ZatcaDashboard extends Component {
    static template = "pos_zatca_async_dashboard_owl.ZatcaDashboard";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            loading: true,
            counters: { pending: 0, sent: 0, failed: 0 },
            latestOrders: [],
        });

        onWillStart(async () => {
            await this.loadDashboard();
        });
    }

    async loadDashboard() {
        this.state.loading = true;
        try {
            const data = await this.orm.call("pos.order", "get_zatca_dashboard_data", []);
            this.state.counters = data.counters || { pending: 0, sent: 0, failed: 0 };
            this.state.latestOrders = data.latest_orders || [];
        } catch (error) {
            this.notification.add("Failed to load ZATCA dashboard data.", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onRefreshClick() {
        await this.loadDashboard();
        this.notification.add("Statistics refreshed.", { type: "success" });
    }
}

registry.category("actions").add(
    "pos_zatca_async_dashboard_owl.zatca_dashboard_action",
    ZatcaDashboard
);
/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ZatcaDashboard extends Component {
    static template = "pos_zatca_async_dashboard_owl.ZatcaDashboard";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            counters: {
                pending: 0,
                sent: 0,
                failed: 0,
            },
            latestOrders: [],
        });

        onWillStart(async () => {
            await this._loadDashboard();
        });
    }

    async _loadDashboard() {
        this.state.loading = true;
        try {
            const data = await this.orm.call("pos.order", "get_zatca_dashboard_data", []);
            this.state.counters = data.counters || { pending: 0, sent: 0, failed: 0 };
            this.state.latestOrders = data.latest_orders || [];
        } catch (error) {
            this.notification.add("Failed to load ZATCA dashboard data.", {
                type: "danger",
            });
            throw error;
        } finally {
            this.state.loading = false;
        }
    }

    async onRefreshClick() {
        await this._loadDashboard();
        this.notification.add("Statistics refreshed.", { type: "success" });
    }
}

registry.category("actions").add("pos_zatca_async_dashboard_owl.zatca_dashboard_action", ZatcaDashboard);