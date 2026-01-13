/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class PropertyFormView extends Component {
    static template = "app_one.PropertyFormView";

    // setup() {
    //     this.orm = useService("orm");
    //     this.actionService = useService("action");
    //     this.notification = useService("notification");

    //     this.state = useState({
    //         isLoading: false,
    //         isSaving: false,
    //         propertyId: null,
    //         formData: {
    //             name: "",
    //             postcode: "",
    //             description: "",
    //             bedrooms: 1,
    //             living_area: 0,
    //             facades: 0,
    //             garage: false,
    //             garden: false,
    //             garden_area: 0,
    //             garden_orientation: "north",
    //             expected_price: 0.0,
    //             selling_price: 0.0,
    //             date_availability: this.getTodayDate(),
    //             expected_date_selling: "",
    //             state: "draft",
    //             owner_id: null,
    //             user_id: null,
    //         },
    //         owners: [],
    //         users: [],
    //         states: [
    //             { value: 'draft', label: 'Draft' },
    //             { value: 'pending', label: 'Pending' },
    //             { value: 'sold', label: 'Sold' },
    //             { value: 'closed', label: 'Closed' }
    //         ],
    //         gardenOrientations: [
    //             { value: 'north', label: 'North' },
    //             { value: 'south', label: 'South' },
    //             { value: 'east', label: 'East' },
    //             { value: 'west', label: 'West' },
    //             { value: 'northeast', label: 'Northeast' },
    //             { value: 'southeast', label: 'Southeast' },
    //             { value: 'southwest', label: 'Southwest' },
    //             { value: 'northwest', label: 'Northwest' },
    //             { value: 'no_garden', label: 'No Garden' }
    //         ],
    //         errors: {}
    //     });

    //     onWillStart(async () => {
    //         await this.loadInitialData();
    //     });
    // }

    // async loadInitialData() {
    //     try {
    //         this.state.isLoading = true;

    //         const [owners, users] = await Promise.all([
    //             this.orm.searchRead("owner", [], ["id", "name"], { limit: 100, order: "name" }),
    //             this.orm.searchRead("res.users", [], ["id", "name"], { limit: 100, order: "name" })
    //         ]);

    //         this.state.owners = owners;
    //         this.state.users = users;

    //         const propertyId = this.props.context?.property_id;
    //         if (propertyId) {
    //             await this.loadProperty(propertyId);
    //         }
    //     } catch (error) {
    //         console.error("Error loading data:", error);
    //         this.notification.add("Failed to load form data", { type: "danger" });
    //     } finally {
    //         this.state.isLoading = false;
    //     }
    // }
    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            isLoading: false,
            isSaving: false,
            propertyId: null,
            formData: {
                name: "",
                postcode: "",
                description: "",
                bedrooms: 1,
                living_area: 0,
                facades: 0,
                garage: false,
                garden: false,
                garden_area: 0,
                garden_orientation: "north",
                expected_price: 0.0,
                selling_price: 0.0,
                date_availability: this.getTodayDate(),
                expected_date_selling: "",
                state: "draft",
                owner_id: null,
                user_id: null,
            },
            owners: [],
            users: [],
            states: [
                { value: 'draft', label: 'Draft' },
                { value: 'pending', label: 'Pending' },
                { value: 'sold', label: 'Sold' },
                { value: 'closed', label: 'Closed' }
            ],
            gardenOrientations: [
                { value: 'north', label: 'North' },
                { value: 'south', label: 'South' },
                { value: 'east', label: 'East' },
                { value: 'west', label: 'West' },
                { value: 'northeast', label: 'Northeast' },
                { value: 'southeast', label: 'Southeast' },
                { value: 'southwest', label: 'Southwest' },
                { value: 'northwest', label: 'Northwest' },
                { value: 'no_garden', label: 'No Garden' }
            ],
            errors: {}
        });

        onWillStart(async () => {
            await this.loadInitialData();
        });
    }
    // async loadInitialData() {
    //     try {
    //         this.state.isLoading = true;

    //         const [owners, users] = await Promise.all([
    //             this.orm.searchRead("owner", [], ["id", "name"], { limit: 100, order: "name" }),
    //             this.orm.searchRead("res.users", [], ["id", "name"], { limit: 100, order: "name" })
    //         ]);

    //         this.state.owners = owners;
    //         this.state.users = users;

    //         // ✅ جرب الطريقتين
    //         const propertyId = this.props.action?.context?.property_id ||
    //             this.env.config?.actionContext?.property_id;

    //         console.log("Property ID received:", propertyId);
    //         console.log("Props:", this.props);
    //         console.log("Context:", this.env.config);

    //         if (propertyId) {
    //             await this.loadProperty(propertyId);
    //         }
    //     } catch (error) {
    //         console.error("Error loading data:", error);
    //         this.notification.add("Failed to load form data", { type: "danger" });
    //     } finally {
    //         this.state.isLoading = false;
    //     }
    // }

    async loadInitialData() {
        try {
            this.state.isLoading = true;

            const [owners, users] = await Promise.all([
                this.orm.searchRead("owner", [], ["id", "name"], { limit: 100, order: "name" }),
                this.orm.searchRead("res.users", [], ["id", "name"], { limit: 100, order: "name" })
            ]);

            this.state.owners = owners;
            this.state.users = users;

            // ✅ الطريقة الصحيحة للحصول على property_id
            const propertyId = this.props.action?.context?.property_id;

            console.log("=== DEBUG INFO ===");
            console.log("Property ID:", propertyId);
            console.log("Full props:", JSON.stringify(this.props, null, 2));
            console.log("Action context:", this.props.action?.context);
            console.log("==================");

            if (propertyId) {
                await this.loadProperty(propertyId);
            }
        } catch (error) {
            console.error("Error loading data:", error);
            this.notification.add("Failed to load form data", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    async loadProperty(propertyId) {
        try {
            const property = await this.orm.read(
                "property",
                [propertyId],
                Object.keys(this.state.formData)
            );

            if (property && property.length > 0) {
                this.state.propertyId = propertyId;
                Object.assign(this.state.formData, property[0]);

                if (property[0].owner_id) {
                    this.state.formData.owner_id = property[0].owner_id[0];
                }
                if (property[0].user_id) {
                    this.state.formData.user_id = property[0].user_id[0];
                }
            }
        } catch (error) {
            console.error("Error loading property:", error);
            this.notification.add("Failed to load property", { type: "danger" });
        }
    }

    validateForm() {
        const errors = {};

        if (!this.state.formData.name || this.state.formData.name.trim() === "") {
            errors.name = "Name is required";
        }

        if (!this.state.formData.postcode || this.state.formData.postcode.trim() === "") {
            errors.postcode = "Postcode is required";
        }

        if (this.state.formData.bedrooms <= 0) {
            errors.bedrooms = "Bedrooms must be greater than zero";
        }

        if (this.state.formData.expected_price < 0) {
            errors.expected_price = "Expected price cannot be negative";
        }

        this.state.errors = errors;
        return Object.keys(errors).length === 0;
    }

    cleanFormData(data) {
        const cleaned = { ...data };

        const dateFields = ['date_availability', 'expected_date_selling'];
        dateFields.forEach(field => {
            if (cleaned[field] === "" || cleaned[field] === null) {
                cleaned[field] = false;
            }
        });

        const many2oneFields = ['owner_id', 'user_id'];
        many2oneFields.forEach(field => {
            if (cleaned[field] === "" || cleaned[field] === null || cleaned[field] === 0) {
                cleaned[field] = false;
            }
        });

        return cleaned;
    }

    async saveProperty() {
        try {
            if (!this.validateForm()) {
                this.notification.add("Please fix the errors before saving", { type: "danger" });
                return;
            }

            this.state.isSaving = true;

            const data = this.cleanFormData(this.state.formData);

            let recordId;
            if (this.state.propertyId) {
                await this.orm.write("property", [this.state.propertyId], data);
                recordId = this.state.propertyId;
            } else {
                const result = await this.orm.create("property", [data]);
                recordId = result[0];
                this.state.propertyId = recordId;
            }

            this.notification.add("Property saved successfully!", { type: "success" });

            await this.goBackToList();
        } catch (error) {
            console.error("Error saving:", error);
            this.notification.add("Failed to save property: " + error.message, { type: "danger" });
        } finally {
            this.state.isSaving = false;
        }
    }

    async goBackToList() {
        await this.actionService.doAction({
            type: "ir.actions.client",
            tag: "app_one.property_list_view",
            name: "Properties",
            target: "current",
        });
    }

    getTodayDate() {
        const today = new Date();
        return today.toISOString().split('T')[0];
    }

    getDiff() {
        return this.state.formData.selling_price - this.state.formData.expected_price;
    }
}

registry.category("actions").add("app_one.property_form_view", PropertyFormView);