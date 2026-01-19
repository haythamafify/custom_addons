/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class CRMLeadCreator extends Component {
    static template = "counter.CRMLeadCreator";
    
    setup() {
        console.log("🟢 CRMLeadCreator setup started");
        
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.state = useState({
            leads: [],
            latestLead: null,
            loading: false
        });
        
        console.log("🟢 CRMLeadCreator setup completed");
        
        // Load leads when component mounts
        this.loadLatestLead();
    }
    
    async createLead() {
        console.log("🟡 Creating new lead...");
        
        const leadData = {
            name: "عميل جديد - " + new Date().toLocaleString('ar-EG'),
            email_from: "customer@example.com",
            phone: "01234567890",
            contact_name: "أحمد محمد"
        };
        
        this.state.loading = true;
        
        try {
            const leadId = await this.orm.create("crm.lead", [leadData]);
            
            console.log("✅ Lead created successfully! ID:", leadId);
            
            this.notification.add("✅ تم إنشاء Lead بنجاح برقم: " + leadId, {
                type: "success"
            });
            
            await this.loadLatestLead();
        } catch (error) {
            console.error("❌ Error creating lead:", error);
            this.notification.add("❌ فشل في إنشاء Lead: " + error.message, {
                type: "danger"
            });
        } finally {
            this.state.loading = false;
        }
    }
    
    async loadLatestLead() {
        console.log("🟡 Loading latest lead...");
        
        this.state.loading = true;
        
        try {
            const leads = await this.orm.searchRead(
                "crm.lead",
                [],
                ["name", "email_from", "phone", "contact_name", "create_date"],
                1
            );
            
            if (leads.length > 0) {
                this.state.latestLead = leads[0];
                this.state.leads = leads;
                console.log("✅ Latest lead loaded:", leads[0]);
            } else {
                this.state.latestLead = null;
                console.log("⚠️ No leads found");
            }
        } catch (error) {
            console.error("❌ Error loading leads:", error);
            this.notification.add("⚠️ فشل في تحميل البيانات: " + error.message, {
                type: "warning"
            });
        } finally {
            this.state.loading = false;
        }
    }
}

// Register as a client action
registry.category("actions").add("counter.crm_lead_creator", CRMLeadCreator);
console.log("✅ CRMLeadCreator registered as action!");