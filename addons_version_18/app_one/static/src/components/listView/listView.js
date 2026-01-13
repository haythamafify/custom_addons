/** @odoo-module **/

import { Component, useState, onWillStart, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { debounce } from "@web/core/utils/timing";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

export class PropertyListView extends Component {
    static template = "app_one.PropertyListView";

    setup() {
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this.notification = useService("notification");

        this.tableRef = useRef("tableContainer");

        this.state = useState({
            records: [],
            isLoading: true,
            isDeleting: null,
            hasError: false,
            errorMessage: "",
            currentPage: 1,
            pageSize: 20,
            totalRecords: 0,
            searchQuery: "",
            filterState: "all",
            sortField: "ref",
            sortOrder: "desc",
            columnSelectorOpen: false,
            selectedRecords: new Set(),
            visibleColumns: {
                ref: true,
                name: true,
                postcode: false,
                user: true,
                dateAvailability: true,
                expectedDateSelling: false,
                sellingPrice: false,
                expectedPrice: false,
                diff: false,
                bedrooms: false,
                state: false,
                owner: false,
            }
        });

        this.columnLabels = {
            ref: 'Ref',
            name: 'Name',
            postcode: 'Postcode',
            user: 'User',
            dateAvailability: 'Date Availability',
            expectedDateSelling: 'Expected Date Selling',
            sellingPrice: 'Selling Price',
            expectedPrice: 'Expected Price',
            diff: 'Diff',
            bedrooms: 'Bedrooms',
            state: 'State',
            owner: 'Owner',
        };

        this.debouncedSearch = debounce(this.performSearch.bind(this), 300);

        onWillStart(async () => {
            await this.loadProperties();
        });

        onWillUnmount(() => {
            if (this.debouncedSearch.cancel) {
                this.debouncedSearch.cancel();
            }
        });
    }

    // ============================================================================
    // Multi-Select Functions
    // ============================================================================

    get isAllSelected() {
        return this.state.records.length > 0 && 
               this.state.records.every(r => this.state.selectedRecords.has(r.id));
    }

    get hasSelection() {
        return this.state.selectedRecords.size > 0;
    }

    get selectedCount() {
        return this.state.selectedRecords.size;
    }

    toggleSelectAll() {
        if (this.isAllSelected) {
            this.state.selectedRecords = new Set();
        } else {
            this.state.selectedRecords = new Set(this.state.records.map(r => r.id));
        }
    }

    toggleSelectRecord(recordId) {
        const newSelection = new Set(this.state.selectedRecords);
        if (newSelection.has(recordId)) {
            newSelection.delete(recordId);
        } else {
            newSelection.add(recordId);
        }
        this.state.selectedRecords = newSelection;
    }

    isRecordSelected(recordId) {
        return this.state.selectedRecords.has(recordId);
    }

    clearSelection() {
        this.state.selectedRecords = new Set();
    }

    async deleteSelected() {
        if (this.state.selectedRecords.size === 0) {
            this.notification.add("No records selected", { type: "warning" });
            return;
        }

        try {
            const confirmed = await new Promise((resolve) => {
                this.dialogService.add(ConfirmationDialog, {
                    title: "Delete Selected Properties",
                    body: `Are you sure you want to delete ${this.state.selectedRecords.size} selected properties?`,
                    confirm: () => resolve(true),
                    cancel: () => resolve(false),
                    confirmLabel: "Delete All",
                    cancelLabel: "Cancel",
                });
            });

            if (!confirmed) return;

            const idsToDelete = Array.from(this.state.selectedRecords);
            await this.orm.unlink("property", idsToDelete);
            
            this.state.selectedRecords = new Set();
            await this.loadProperties();

            this.notification.add(`${idsToDelete.length} properties deleted successfully`, { type: "success" });
        } catch (error) {
            console.error("Error deleting properties:", error);
            this.notification.add(`Failed to delete properties: ${error.message}`, { type: "danger" });
        }
    }

    // ============================================================================
    // Column Management
    // ============================================================================

    get visibleColumnCount() {
        return Object.values(this.state.visibleColumns).filter(v => v).length;
    }

    toggleColumnSelector() {
        this.state.columnSelectorOpen = !this.state.columnSelectorOpen;
    }

    toggleColumn(columnKey) {
        this.state.visibleColumns[columnKey] = !this.state.visibleColumns[columnKey];
    }

    isColumnVisible(columnKey) {
        return this.state.visibleColumns[columnKey];
    }

    // ============================================================================
    // Data Loading
    // ============================================================================

    async loadProperties() {
        try {
            this.state.isLoading = true;
            this.state.hasError = false;
            
            // Clear selection when loading new page
            this.state.selectedRecords = new Set();

            const domain = this.buildDomain();
            const offset = (this.state.currentPage - 1) * this.state.pageSize;

            const [records, totalCount] = await Promise.all([
                this.orm.searchRead(
                    "property",
                    domain,
                    [
                        "id", "ref", "name", "postcode", "user_id",
                        "date_availability", "expected_date_selling",
                        "selling_price", "expected_price", "diff",
                        "bedrooms", "state", "owner_id", "is_late"
                    ],
                    {
                        limit: this.state.pageSize,
                        offset: offset,
                        order: `${this.state.sortField} ${this.state.sortOrder}`
                    }
                ),
                this.orm.searchCount("property", domain)
            ]);

            this.state.records = records;
            this.state.totalRecords = totalCount;
        } catch (error) {
            console.error("Error loading properties:", error);
            this.state.hasError = true;
            this.state.errorMessage = error.message || "Failed to load properties";
            this.notification.add("Failed to load properties. Please try again.", { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    buildDomain() {
        const domain = [];

        if (this.state.searchQuery.trim()) {
            domain.push('|', '|');
            domain.push(['name', 'ilike', this.state.searchQuery]);
            domain.push(['ref', 'ilike', this.state.searchQuery]);
            domain.push(['postcode', 'ilike', this.state.searchQuery]);
        }

        if (this.state.filterState !== "all") {
            domain.push(['state', '=', this.state.filterState]);
        }

        return domain;
    }

    // ============================================================================
    // Search and Filter
    // ============================================================================

    onSearchInput(event) {
        this.state.searchQuery = event.target.value;
        this.state.currentPage = 1;
        this.debouncedSearch();
    }

    async performSearch() {
        await this.loadProperties();
    }

    onFilterChange(event) {
        this.state.filterState = event.target.value;
        this.state.currentPage = 1;
        this.loadProperties();
    }

    // ============================================================================
    // Sorting
    // ============================================================================

    onSort(field) {
        if (this.state.sortField === field) {
            this.state.sortOrder = this.state.sortOrder === "asc" ? "desc" : "asc";
        } else {
            this.state.sortField = field;
            this.state.sortOrder = "asc";
        }
        this.loadProperties();
    }

    getSortIcon(field) {
        if (this.state.sortField !== field) return '';
        return this.state.sortOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    }

    // ============================================================================
    // Pagination
    // ============================================================================

    get totalPages() {
        return Math.ceil(this.state.totalRecords / this.state.pageSize);
    }

    get canGoPrevious() {
        return this.state.currentPage > 1;
    }

    get canGoNext() {
        return this.state.currentPage < this.totalPages;
    }

    async goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
            this.state.currentPage = page;
            await this.loadProperties();

            if (this.tableRef.el) {
                this.tableRef.el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }

    async previousPage() {
        if (this.canGoPrevious) {
            await this.goToPage(this.state.currentPage - 1);
        }
    }

    async nextPage() {
        if (this.canGoNext) {
            await this.goToPage(this.state.currentPage + 1);
        }
    }

    // ============================================================================
    // CRUD Operations
    // ============================================================================

    async createProperty() {
        try {
            await this.actionService.doAction({
                type: "ir.actions.client",
                tag: "app_one.property_form_view",
                name: "New Property",
                target: "current",
                context: { default_state: "draft" }
            });
        } catch (error) {
            console.error("Error opening form:", error);
            this.notification.add("Failed to open property form", { type: "danger" });
        }
    }

    async deleteProperty(record) {
        try {
            const confirmed = await new Promise((resolve) => {
                this.dialogService.add(ConfirmationDialog, {
                    title: "Delete Property",
                    body: `Are you sure you want to delete "${record.name}" (${record.ref})?`,
                    confirm: () => resolve(true),
                    cancel: () => resolve(false),
                    confirmLabel: "Delete",
                    cancelLabel: "Cancel",
                });
            });

            if (!confirmed) return;

            this.state.isDeleting = record.id;
            await this.orm.unlink("property", [record.id]);
            await this.loadProperties();

            this.notification.add(`Property "${record.name}" deleted successfully`, { type: "success" });
        } catch (error) {
            console.error("Error deleting property:", error);
            this.notification.add(`Failed to delete property: ${error.message}`, { type: "danger" });
        } finally {
            this.state.isDeleting = null;
        }
    }

    async editProperty(recordId) {
        try {
            await this.actionService.doAction({
                type: "ir.actions.client",
                tag: "app_one.property_form_view",
                name: "Edit Property",
                target: "current",
            }, {
                additionalContext: {
                    property_id: recordId
                }
            });
        } catch (error) {
            console.error("Error opening form:", error);
            this.notification.add("Failed to open property form", { type: "danger" });
        }
    }

    async retryLoad() {
        await this.loadProperties();
    }

    // ============================================================================
    // Helper Functions
    // ============================================================================

    getUserName(user_id) {
        return user_id && user_id.length > 1 ? user_id[1] : "N/A";
    }

    getOwnerName(owner_id) {
        return owner_id && owner_id.length > 1 ? owner_id[1] : "N/A";
    }

    formatPrice(price) {
        if (!price) return "$0";
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(price);
    }

    formatDate(date) {
        if (!date) return "N/A";
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    getStateBadgeClass(state) {
        const stateMap = {
            'draft': 'badge-secondary',
            'pending': 'badge-warning',
            'sold': 'badge-success',
            'closed': 'badge-dark'
        };
        return `badge ${stateMap[state] || 'badge-info'}`;
    }

    getStateLabel(state) {
        const labels = {
            'draft': 'Draft',
            'pending': 'Pending',
            'sold': 'Sold',
            'closed': 'Closed'
        };
        return labels[state] || state;
    }
}

registry.category("actions").add("app_one.property_list_view", PropertyListView);