/** @odoo-module **/
import { Component, useSubEnv, useState, onWillStart } from "@odoo/owl";  
import { useService } from "@web/core/utils/hooks";  
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";

export class OdooDashboard extends Component {
    static template = "owl.OdooDashboardTemplate";
    static components = { Layout };

    setup() {
        useSubEnv({ config: this.env.config });
        
        // ✅ استخدم useState للبيانات
        this.state = useState({
            dashboardData: {
                Partners: 0,
                Customers: 0,
                Individuals: 0,
                Locations: 0
            },
            isLoading: false,
            lastUpdate: null
        });
        
        // الحصول على الخدمة
        this.dashboardService = useService("owldashboardsService");
        
        // ✅ تحميل البيانات أول مرة
        onWillStart(async () => {
            await this.loadDashboardData();
        });
        
        // ✅ تحديث تلقائي كل 30 ثانية
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000); // 30 ثانية
    }
    
    // ✅ Function لتحميل البيانات
    async loadDashboardData() {
        try {
            this.state.isLoading = true;
            
            const data = await this.dashboardService.fetchDashboardData();
            
            // ✅ تحديث الـ state - الـ UI هيتحدث تلقائياً!
            this.state.dashboardData = data;
            this.state.lastUpdate = new Date().toLocaleTimeString('ar-EG');
            this.state.isLoading = false;
            
            console.log("Dashboard updated:", this.state.dashboardData);
            
        } catch (error) {
            console.error("Error loading dashboard:", error);
            this.state.isLoading = false;
        }
    }
    
    // ✅ Function للتحديث اليدوي (من الزر)
    async refreshData() {
        await this.loadDashboardData();
    }

    get getowl_basicService() {
        const basicService = this.env.services.basicService;
        return basicService || {};
    }

    stringifyObject(obj) {
        return JSON.stringify(obj);
    }
    
    // ✅ تنظيف الـ interval عند إغلاق الـ Component
    willUnmount() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }
}

registry.category("actions").add("owl.odoo_dashboard", OdooDashboard);