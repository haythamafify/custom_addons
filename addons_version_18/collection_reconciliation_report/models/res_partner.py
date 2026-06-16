from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    related_collections_count = fields.Integer(
        string="Related Collections",
        compute="_compute_related_collections_count",
    )

    def _compute_related_collections_count(self):
        report_model = self.env["collection.reconciliation.report"]
        grouped = report_model.read_group(
            [("partner_id", "in", self.ids)],
            ["partner_id"],
            ["partner_id"],
        )
        mapped = {entry["partner_id"][0]: entry["partner_id_count"] for entry in grouped if entry["partner_id"]}
        for partner in self:
            partner.related_collections_count = mapped.get(partner.id, 0)

    def action_open_related_collections(self):
        self.ensure_one()
        action = self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_report"
        ).read()[0]
        action["domain"] = [("partner_id", "child_of", self.id)]
        action["name"] = _("Related Collections")
        return action
