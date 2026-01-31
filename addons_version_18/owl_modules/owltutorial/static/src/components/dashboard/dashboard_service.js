/** @odoo-module **/
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export const owldashboardsService = {
    dashBoard_data: {},
    
    async start(env) {
        console.log("Owl Dashboards Service started");
        
        try {
            // الطريقة الصحيحة في Odoo 17/18
            const data = await rpc("/owl/dashboard_service", {
                limit: 100
            });
            
            this.dashBoard_data = data;
            console.log("Dashboard data loaded:", this.dashBoard_data);
            
        } catch (error) {
            console.error("Error loading dashboard data:", error);
            
        }
        
        return {
            dashBoard_data: this.dashBoard_data,
        };
    },
};

// تسجيل الخدمة
registry.category("services").add("owldashboardsService", owldashboardsService);