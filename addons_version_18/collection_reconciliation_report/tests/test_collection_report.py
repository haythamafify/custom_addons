from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestCollectionReconciliationReport(TransactionCase):
    def test_report_models_exist(self):
        report = self.env["collection.reconciliation.report"]
        kpi = self.env["collection.reconciliation.report.kpi"]
        history = self.env["collection.reconciliation.refresh.history"]
        self.assertTrue(report._table)
        self.assertTrue(kpi._table)
        self.assertEqual(history._name, "collection.reconciliation.refresh.history")

    def test_materialized_parameter_is_boolean(self):
        report = self.env["collection.reconciliation.report"]
        self.env["ir.config_parameter"].sudo().set_param(
            "collection_report.use_materialized_view",
            "True",
        )
        self.assertTrue(report._is_materialized_view_enabled())
        self.env["ir.config_parameter"].sudo().set_param(
            "collection_report.use_materialized_view",
            "False",
        )
        self.assertFalse(report._is_materialized_view_enabled())

    def test_debug_and_stale_parameters(self):
        report = self.env["collection.reconciliation.report"]
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("collection_report.debug_logging", "True")
        params.set_param("collection_report.stale_after_hours", "12")
        self.assertTrue(report._is_debug_logging_enabled())
        self.assertEqual(report._get_int_param("collection_report.stale_after_hours"), 12)
        self.assertEqual(
            report._get_refresh_lock_key(report._table),
            report._get_refresh_lock_key(report._table),
        )

    def test_smart_button_actions_exist(self):
        partner = self.env["res.partner"].create({"name": "Collection Test Partner"})
        action = partner.action_open_related_collections()
        self.assertEqual(action["res_model"], "collection.reconciliation.report")

    def test_report_refresh_is_safe_when_disabled(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "collection_report.use_materialized_view",
            "False",
        )
        self.assertFalse(
            self.env["collection.reconciliation.report"].refresh_materialized_view()
        )

    def test_refresh_history_creation(self):
        history = self.env["collection.reconciliation.report"]._create_refresh_history(
            "skipped",
            "standard",
            fields.Datetime.now(),
            company_id=self.env.company.id,
            error_message="Skipped in test",
        )
        self.assertEqual(history.status, "skipped")
        self.assertEqual(history.company_id, self.env.company)

    def test_open_refresh_history_action(self):
        action = self.env["collection.reconciliation.report"].action_open_refresh_history()
        self.assertEqual(action["res_model"], "collection.reconciliation.refresh.history")

    def test_kpi_refresh_fields_exist(self):
        fields_map = self.env["collection.reconciliation.report.kpi"]._fields
        self.assertIn("last_refresh_at", fields_map)
        self.assertIn("refresh_status", fields_map)
        self.assertIn("is_stale", fields_map)

    def test_kpi_select_sql_returns_safe_tuple(self):
        """_get_kpi_select_sql must return (str, tuple) — never an f-string with user data."""
        report = self.env["collection.reconciliation.report.kpi"]
        self.env["ir.config_parameter"].sudo().set_param(
            "collection_report.stale_after_hours", "48"
        )
        result = report._get_kpi_select_sql()
        self.assertIsInstance(result, tuple, "_get_kpi_select_sql must return a (sql, params) tuple")
        self.assertEqual(len(result), 2)
        sql_str, params = result
        self.assertIsInstance(sql_str, str)
        self.assertIsInstance(params, tuple)
        # The raw SQL must NOT contain the literal hour value — it must be parameterised.
        self.assertNotIn("48", sql_str, "stale_hours must be a bind param, not interpolated into SQL")
        self.assertIn("%s", sql_str, "SQL must contain a %s bind placeholder for stale_hours")
        self.assertEqual(params[0], 48)

    def test_kpi_select_sql_clamps_extreme_values(self):
        """stale_hours is clamped to [1, 8760] regardless of ir.config_parameter content."""
        report = self.env["collection.reconciliation.report.kpi"]
        for raw, expected in [("0", 1), ("-5", 1), ("99999", 8760), ("24", 24)]:
            self.env["ir.config_parameter"].sudo().set_param(
                "collection_report.stale_after_hours", raw
            )
            _, params = report._get_kpi_select_sql()
            self.assertEqual(
                params[0], expected,
                f"stale_hours={raw!r} should clamp to {expected}, got {params[0]}"
            )

    def test_xlsx_report_registration_exists(self):
        action = self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_report_xlsx"
        )
        self.assertEqual(action.report_type, "xlsx")

    def test_sql_view_fields_have_no_translate(self):
        """SQL-backed readonly fields must not use translate=True (ORM cannot write translations)."""
        report_fields = self.env["collection.reconciliation.report"]._fields
        no_translate = ["payment_name", "invoice_name", "product_names", "memo"]
        for fname in no_translate:
            field = report_fields.get(fname)
            self.assertIsNotNone(field, f"Field {fname!r} should exist")
            self.assertFalse(
                getattr(field, "translate", False),
                f"Field {fname!r} on SQL view must not have translate=True",
            )
        kpi_fields = self.env["collection.reconciliation.report.kpi"]._fields
        field = kpi_fields.get("top_collectors")
        self.assertFalse(
            getattr(field, "translate", False),
            "top_collectors on SQL view must not have translate=True",
        )
