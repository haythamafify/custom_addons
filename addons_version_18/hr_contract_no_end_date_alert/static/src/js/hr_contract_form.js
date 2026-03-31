/** @odoo-module **/

import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(FormController.prototype, {

    async beforeExecuteActionButton(clickParams) {
        if (this.props.resModel === "hr.contract") {
            const record = this.model.root;
            const dateEnd = record.data.date_end;
            const skipCheck = record.data.skip_end_date_check;

            if (!dateEnd && !skipCheck) {
                const confirmed = await this.dialogService.add(ConfirmationDialog, {
                    title: _t("⚠️ Contract End Date Missing"),
                    body: _t(
                        "This contract has no end date!\n\n" +
                        "The contract will become open-ended (no end date).\n\n" +
                        "Do you want to continue saving?"
                    ),
                    confirm: () => {
                        record.update({ skip_end_date_check: true });
                    },
                    cancel: () => {},
                    confirmLabel: _t("Yes, Save"),
                    cancelLabel: _t("No, Cancel"),
                });

                if (!confirmed) {
                    return false;
                }
            }
        }

        return super.beforeExecuteActionButton(...arguments);
    },

    async saveButtonClicked(params = {}) {
        if (this.props.resModel === "hr.contract") {
            const record = this.model.root;
            const dateEnd = record.data.date_end;
            const skipCheck = record.data.skip_end_date_check;

            if (!dateEnd && !skipCheck) {
                try {
                    await this.dialogService.add(ConfirmationDialog, {
                        title: _t("⚠️ Contract End Date Missing"),
                        body: _t(
                            "This contract has no end date!\n\n" +
                            "The contract will become open-ended (no end date).\n\n" +
                            "Do you want to continue saving?"
                        ),
                        confirm: async () => {
                            record.update({ skip_end_date_check: true });
                            await super.saveButtonClicked.call(this, params);
                        },
                        cancel: () => {},
                        confirmLabel: _t("Yes, Save"),
                        cancelLabel: _t("No, Cancel"),
                    });
                } catch (error) {
                    return;
                }

                return;
            }
        }

        return super.saveButtonClicked(params);
    },
});