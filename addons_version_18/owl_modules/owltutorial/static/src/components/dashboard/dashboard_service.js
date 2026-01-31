/** @odoo-module **/
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

export const owldashboardsService = {
    dependencies: [],
    
    async start(env) {
        console.log("Owl Dashboards Service started");
        
        // ✅ بدل reactive، هنرجع functions بس
        const service = {
            // Function لجلب البيانات
            async fetchDashboardData() {
                try {
                    console.log("Fetching dashboard data...");
                    
                    const data = await rpc("/owl/dashboard_service", {
                        limit: 100
                    });
                    
                    console.log("Dashboard data fetched:", data);
                    return data;
                    
                } catch (error) {
                    console.error("Error loading dashboard data:", error);
                    throw error;
                }
            }
        };
        
        return service;
    },
};

// تسجيل الخدمة
registry.category("services").add("owldashboardsService", owldashboardsService);