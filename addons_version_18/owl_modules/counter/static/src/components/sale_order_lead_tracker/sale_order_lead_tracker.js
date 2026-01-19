/** @odoo-module **/
import { Component, useState, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class SaleOrderLeadTracker extends Component {
    static template = "counter.SaleOrderLeadTracker";

    setup() {
        console.log("SaleOrderLeadTracker setup started");

        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            saleOrders: [],
            loading: false
        });

        onMounted(() => {
            this.loadSaleOrders();
        });
    }

    async loadSaleOrders() {
        console.log("Loading sale orders...");
        this.state.loading = true;

        try {
            const orders = await this.orm.searchRead(
                "sale.order",
                [],
                ["name", "partner_id", "state", "amount_total", "opportunity_id", "date_order"],
                80
            );

            console.log("Sale orders loaded:", orders.length);

            // Get opportunity details for each order that has opportunity_id
            for (let order of orders) {
                if (order.opportunity_id && order.opportunity_id[0]) {
                    try {
                        const opportunities = await this.orm.searchRead(
                            "crm.lead",
                            [["id", "=", order.opportunity_id[0]]],
                            ["probability"],
                            1
                        );

                        if (opportunities && opportunities.length > 0) {
                            order.probability = opportunities[0].probability;
                        } else {
                            order.probability = 0;
                        }
                    } catch (error) {
                        console.error("Error loading opportunity for order:", order.name, error);
                        order.probability = 0;
                    }
                } else {
                    order.probability = 0;
                }
            }

            this.state.saleOrders = orders;
            console.log("Sale orders with probability:", this.state.saleOrders);

        } catch (error) {
            console.error("Error loading sale orders:", error);
            this.notification.add("Failed to load sale orders: " + error.message, {
                type: "danger"
            });
        } finally {
            this.state.loading = false;
        }
    }

    getMessageForOrder(order) {
        if (order.state === "sale") {
            return {
                text: "Well Done!",
                class: "success"
            };
        }

        if (order.state !== "sale" && order.probability > 50) {
            return {
                text: "You can do better!",
                class: "danger"
            };
        }

        return null;
    }

    formatState(state) {
        const stateMap = {
            "draft": "Draft",
            "sent": "Quotation Sent",
            "sale": "Sales Order",
            "done": "Locked",
            "cancel": "Cancelled"
        };
        return stateMap[state] || state;
    }

    async refreshOrders() {
        await this.loadSaleOrders();
        this.notification.add("Sale orders refreshed successfully", {
            type: "success"
        });
    }
}

registry.category("actions").add("counter.sale_order_lead_tracker", SaleOrderLeadTracker);
console.log("SaleOrderLeadTracker registered as action!");