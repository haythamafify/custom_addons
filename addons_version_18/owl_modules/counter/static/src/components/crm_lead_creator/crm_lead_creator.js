/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";

export class CRMLeadCreator extends Component {
    static template = "counter.CRMLeadCreator";

    setup() {
        console.log("CRMLeadCreator setup started");

        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            // Form inputs
            formData: {
                name: "",
                email_from: "",
                phone: "",
                contact_name: ""
            },
            // Latest lead data
            leads: [],
            latestLead: null,
            loading: false,
            leadCount: 0  // Track number of leads for refresh detection
        });

        console.log("CRMLeadCreator setup completed");

        // Load leads when component mounts
        this.loadLatestLead();
    }

    // Update form field
    updateField(field, event) {
        this.state.formData[field] = event.target.value;
    }

    // Validate form
    validateForm() {
        const { name, email_from, phone, contact_name } = this.state.formData;

        if (!name.trim()) {
            this.notification.add("يرجى إدخال اسم العميل", { type: "warning" });
            return false;
        }

        if (!email_from.trim()) {
            this.notification.add("يرجى إدخال البريد الإلكتروني", { type: "warning" });
            return false;
        }

        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email_from)) {
            this.notification.add("البريد الإلكتروني غير صحيح", { type: "warning" });
            return false;
        }

        if (!phone.trim()) {
            this.notification.add("يرجى إدخال رقم الهاتف", { type: "warning" });
            return false;
        }

        if (!contact_name.trim()) {
            this.notification.add("يرجى إدخال اسم جهة الاتصال", { type: "warning" });
            return false;
        }

        return true;
    }

    // Clear form
    clearForm() {
        this.state.formData = {
            name: "",
            email_from: "",
            phone: "",
            contact_name: ""
        };
    }

    async createLead() {
        console.log("Creating new lead...");

        // Validate form
        if (!this.validateForm()) {
            return;
        }

        const leadData = {
            name: this.state.formData.name,
            email_from: this.state.formData.email_from,
            phone: this.state.formData.phone,
            contact_name: this.state.formData.contact_name
        };

        this.state.loading = true;

        try {
            const leadId = await this.orm.create("crm.lead", [leadData]);

            console.log("Lead created successfully! ID:", leadId);

            this.notification.add("تم إنشاء Lead بنجاح برقم: " + leadId, {
                type: "success"
            });

            // Clear form after success
            this.clearForm();

            // Force refresh after short delay
            setTimeout(() => {
                this.loadLatestLead(true);
            }, 800);

        } catch (error) {
            console.error("Error creating lead:", error);
            this.notification.add("فشل في إنشاء Lead: " + error.message, {
                type: "danger"
            });
        } finally {
            this.state.loading = false;
        }
    }

    async loadLatestLead(forceRefresh = false) {
        console.log("Loading latest lead... (force:", forceRefresh, ")");

        this.state.loading = true;

        try {
            // Get ALL leads first, then sort manually
            const allLeads = await this.orm.searchRead(
                "crm.lead",
                [],
                ["name", "email_from", "phone", "contact_name", "create_date"],
                80  // Get more leads to ensure we get the latest
            );

            console.log("Total leads loaded:", allLeads.length);

            if (allLeads && allLeads.length > 0) {
                // Sort by ID descending (latest first)
                allLeads.sort((a, b) => b.id - a.id);

                const latest = allLeads[0];

                // Check if this is actually a new lead
                if (forceRefresh || !this.state.latestLead || latest.id !== this.state.latestLead.id) {
                    this.state.latestLead = latest;
                    this.state.leads = allLeads;
                    this.state.leadCount = allLeads.length;
                    console.log("Latest lead updated! ID:", latest.id, "Name:", latest.name);
                } else {
                    console.log("Same lead as before, no update needed");
                }
            } else {
                this.state.latestLead = null;
                this.state.leadCount = 0;
                console.log("No leads found in database");
            }
        } catch (error) {
            console.error("Error loading leads:", error);
            this.notification.add("فشل في تحميل البيانات: " + error.message, {
                type: "warning"
            });
        } finally {
            this.state.loading = false;
        }
    }
}

// Register as a client action
registry.category("actions").add("counter.crm_lead_creator", CRMLeadCreator);
console.log("CRMLeadCreator registered as action!");