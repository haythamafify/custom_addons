from odoo import _, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_allocations_count = fields.Integer(
        string="Payment Allocations",
        compute="_compute_payment_allocations_count",
    )

    def _compute_payment_allocations_count(self):
        report_model = self.env["collection.reconciliation.report"]
        grouped = report_model.read_group(
            [("payment_id", "in", self.ids)],
            ["payment_id"],
            ["payment_id"],
        )
        mapped = {entry["payment_id"][0]: entry["payment_id_count"] for entry in grouped if entry["payment_id"]}
        for payment in self:
            payment.payment_allocations_count = mapped.get(payment.id, 0)

    def action_open_payment_allocations(self):
        self.ensure_one()
        action = self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_report"
        ).read()[0]
        action["domain"] = [("payment_id", "=", self.id)]
        action["name"] = _("Payment Allocations")
        return action
