from odoo import _, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    collection_analytics_count = fields.Integer(
        string="Collection Analytics",
        compute="_compute_collection_analytics_count",
    )

    def _compute_collection_analytics_count(self):
        report_model = self.env["collection.reconciliation.report"]
        invoice_moves = self.filtered(lambda move: move.is_invoice(include_receipts=True))
        entry_moves = self - invoice_moves

        invoice_counts = {}
        if invoice_moves:
            grouped = report_model.read_group(
                [("invoice_id", "in", invoice_moves.ids)],
                ["invoice_id"],
                ["invoice_id"],
            )
            invoice_counts = {
                item["invoice_id"][0]: item["invoice_id_count"]
                for item in grouped
                if item["invoice_id"]
            }

        line_to_move = {
            line.id: move.id for move in entry_moves for line in move.line_ids
        }
        move_counts = dict.fromkeys(entry_moves.ids, 0)
        if line_to_move:
            grouped = report_model.read_group(
                [("payment_move_line_id", "in", list(line_to_move.keys()))],
                ["payment_move_line_id"],
                ["payment_move_line_id"],
            )
            for item in grouped:
                move_id = line_to_move.get(item["payment_move_line_id"][0])
                if move_id:
                    move_counts[move_id] = move_counts.get(move_id, 0) + item["payment_move_line_id_count"]

        for move in self:
            move.collection_analytics_count = invoice_counts.get(move.id, move_counts.get(move.id, 0))

    def action_open_collection_analytics(self):
        self.ensure_one()
        action = self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_report"
        ).read()[0]
        if self.is_invoice(include_receipts=True):
            action["domain"] = [("invoice_id", "=", self.id)]
            action["name"] = _("Collection Analytics")
        else:
            action["domain"] = [("payment_move_line_id", "in", self.line_ids.ids)]
            action["name"] = _("Payment Allocations")
        return action
