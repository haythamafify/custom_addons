/** @odoo-module **/
import { Component, useSubEnv } from "@odoo/owl";  
import { useService } from "@web/core/utils/hooks";  
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";

export class OdooDashboard extends Component {
    static template = "owl.OdooDashboardTemplate";
    static components = { Layout };

    setup() {
        useSubEnv({ config: this.env.config });
        
        // الحصول على الخدمات
        this.dashboard_services = useService("owldashboardsService");
        console.log("Dashboard Services:", this.dashboard_services);
    }

    get getowl_basicService() {
        console.log("getowl_basicService");
        const basicService = this.env.services.basicService;
        return basicService || {};
    }

    // Helper للوصول لبيانات الـ Dashboard
    get dashboardData() {
        return this.dashboard_services?.dashBoard_data || {};
    }

    stringifyObject(obj) {
        return JSON.stringify(obj);
    }
}

registry.category("actions").add("owl.odoo_dashboard", OdooDashboard);