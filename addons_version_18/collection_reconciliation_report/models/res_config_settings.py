from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    collection_report_use_materialized_view = fields.Boolean(
        string="Use Materialized Collection View",
        config_parameter="collection_report.use_materialized_view",
        help="When enabled, the collection analytics base relation is created as a PostgreSQL materialized view.",
    )
    collection_report_debug_logging = fields.Boolean(
        string="Enable Debug Logging",
        config_parameter="collection_report.debug_logging",
        help="Enable verbose structured logs for diagnostics and performance tracing.",
    )
    collection_report_stale_after_hours = fields.Integer(
        string="Stale Threshold (Hours)",
        config_parameter="collection_report.stale_after_hours",
        default=24,
        help="Dashboard data older than this threshold will be highlighted as stale.",
    )
