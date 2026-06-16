import logging
import time
import zlib

from psycopg2 import sql

from odoo import _, api, fields, models


LOGGER_NAME = "odoo.addons.collection_reconciliation_report"
_logger = logging.getLogger(LOGGER_NAME)


class CollectionReconciliationSqlMixin(models.AbstractModel):
    """Shared SQL helpers and observability for collection analytics."""

    _name = "collection.reconciliation.sql.mixin"
    _description = "Collection Reconciliation SQL Mixin"

    @api.model
    def _is_materialized_view_enabled(self):
        return self._get_bool_param("collection_report.use_materialized_view")

    @api.model
    def _is_debug_logging_enabled(self):
        return self._get_bool_param("collection_report.debug_logging")

    @api.model
    def _get_bool_param(self, key, default="False"):
        value = self.env["ir.config_parameter"].sudo().get_param(key, default=default)
        return str(value).lower() in {"1", "true", "yes", "on"}

    @api.model
    def _get_int_param(self, key, default=24):
        value = self.env["ir.config_parameter"].sudo().get_param(key, default=str(default))
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @api.model
    def _log_structured(self, level, event, **payload):
        if level == "debug" and not self._is_debug_logging_enabled():
            return
        getattr(_logger, level)(
            "%s | %s",
            event,
            ", ".join(f"{key}={value}" for key, value in sorted(payload.items())),
        )

    @api.model
    def _drop_relation(self, relation_name):
        self.env.cr.execute(
            """
            SELECT c.relkind
            FROM pg_class c
            JOIN pg_namespace n
                ON n.oid = c.relnamespace
            WHERE c.relname = %s
                AND n.nspname = current_schema()
            """,
            [relation_name],
        )
        row = self.env.cr.fetchone()
        if not row:
            return
        statement = "DROP MATERIALIZED VIEW IF EXISTS {} CASCADE"
        if row[0] == "v":
            statement = "DROP VIEW IF EXISTS {} CASCADE"
        self.env.cr.execute(sql.SQL(statement).format(sql.Identifier(relation_name)))

    @api.model
    def _create_standard_view(self, relation_name, select_sql, params=None):
        self.env.cr.execute(
            sql.SQL("CREATE OR REPLACE VIEW {} AS ({})").format(
                sql.Identifier(relation_name),
                sql.SQL(select_sql),
            ),
            params or [],
        )

    @api.model
    def _create_materialized_view(self, relation_name, select_sql):
        self.env.cr.execute(
            sql.SQL("CREATE MATERIALIZED VIEW {} AS ({})").format(
                sql.Identifier(relation_name),
                sql.SQL(select_sql),
            )
        )

    @api.model
    def _time_sql(self, label, callback, **payload):
        started_at = time.perf_counter()
        callback()
        elapsed = time.perf_counter() - started_at
        self._log_structured("info", label, duration_seconds=f"{elapsed:.3f}", **payload)
        return elapsed

    @api.model
    def _get_refresh_lock_key(self, relation_name):
        return zlib.crc32(f"{self.env.cr.dbname}:{relation_name}".encode("utf-8")) & 0x7FFFFFFF


class CollectionReconciliationReport(models.Model):
    """SQL-backed analytics model for payment-to-invoice reconciliation."""

    _name = "collection.reconciliation.report"
    _description = "Collection Reconciliation Report"
    _inherit = "collection.reconciliation.sql.mixin"
    _auto = False
    _rec_name = "payment_name"
    _order = "payment_date desc, id desc"

    payment_date = fields.Date(string="Payment Date", readonly=True)
    payment_id = fields.Many2one("account.payment", string="Payment", readonly=True)
    payment_name = fields.Char(string="Payment Reference", readonly=True)
    invoice_id = fields.Many2one("account.move", string="Invoice", readonly=True)
    invoice_name = fields.Char(string="Invoice Number", readonly=True)
    partner_id = fields.Many2one("res.partner", string="Customer", readonly=True)
    salesperson_id = fields.Many2one("res.users", string="Salesperson", readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    journal_id = fields.Many2one("account.journal", string="Journal", readonly=True)
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True)
    collected_amount = fields.Monetary(string="Collected Amount", readonly=True)
    invoice_total = fields.Monetary(string="Invoice Total", readonly=True)
    residual_amount = fields.Monetary(string="Residual Amount", readonly=True)
    invoice_date = fields.Date(string="Invoice Date", readonly=True)
    due_date = fields.Date(string="Due Date", readonly=True)
    payment_delay_days = fields.Integer(string="Payment Delay Days", readonly=True)
    allocation_count = fields.Integer(string="Allocation Count", readonly=True)
    invoice_state = fields.Selection(
        selection=lambda self: self.env["account.move"]._fields["state"].selection,
        string="Invoice Status",
        readonly=True,
    )
    payment_state = fields.Selection(
        selection=lambda self: self.env["account.move"]._fields["payment_state"].selection,
        string="Payment Status",
        readonly=True,
    )
    reconciled_line_id = fields.Many2one("account.move.line", string="Reconciled Line", readonly=True)
    payment_move_line_id = fields.Many2one("account.move.line", string="Payment Move Line", readonly=True)
    invoice_move_line_id = fields.Many2one("account.move.line", string="Invoice Move Line", readonly=True)
    product_names = fields.Char(string="Products", readonly=True)
    memo = fields.Char(string="Memo", readonly=True)

    @api.model
    def _get_report_select_sql(self):
        """Return the SQL body used for the base analytical relation."""

        return """
            /* EXPLAIN guidance:
               1. Validate account_partial_reconcile join selectivity first.
               2. Benchmark pivot-heavy workloads with date, salesperson, and partner groupings.
               3. Use EXPLAIN (ANALYZE, BUFFERS) after every new composite index.

               Recommended indexes for 10M+ move lines / 2M+ reconciliations:
               CREATE INDEX IF NOT EXISTS apr_debit_idx
                   ON account_partial_reconcile (debit_move_id, max_date, amount);
               CREATE INDEX IF NOT EXISTS apr_credit_idx
                   ON account_partial_reconcile (credit_move_id, max_date, amount);
               CREATE INDEX IF NOT EXISTS aml_reconcile_customer_idx
                   ON account_move_line (move_id, partner_id, currency_id)
                   WHERE account_internal_type IN ('asset_receivable', 'liability_payable');
               CREATE INDEX IF NOT EXISTS move_customer_reporting_idx
                   ON account_move (move_type, company_id, partner_id, invoice_user_id, date, invoice_date_due);
               CREATE INDEX IF NOT EXISTS payment_move_idx
                   ON account_payment (move_id, date, company_id);
            */
            WITH product_data AS (
                SELECT
                    aml.move_id AS invoice_id,
                    STRING_AGG(
                        DISTINCT COALESCE(
                            pt.name ->> 'en_US',
                            aml.name
                        ),
                        ', ' ORDER BY COALESCE(
                            pt.name ->> 'en_US',
                            aml.name
                        )
                    ) AS product_names
                FROM account_move_line aml
                LEFT JOIN product_product pp
                    ON pp.id = aml.product_id
                LEFT JOIN product_template pt
                    ON pt.id = pp.product_tmpl_id
                WHERE aml.display_type IS NULL
                    AND aml.product_id IS NOT NULL
                GROUP BY aml.move_id
            ),
            reconcile_base AS (
                SELECT
                    apr.id AS partial_reconcile_id,
                    apr.max_date AS reconciliation_date,
                    apr.amount AS company_amount,
                    apr.debit_amount_currency,
                    apr.credit_amount_currency,
                    dml.id AS debit_line_id,
                    cml.id AS credit_line_id,
                    dml.currency_id AS debit_currency_id,
                    cml.currency_id AS credit_currency_id,
                    dm.id AS debit_move_id,
                    cm.id AS credit_move_id,
                    dm.name AS debit_move_name,
                    cm.name AS credit_move_name,
                    dm.ref AS debit_ref,
                    cm.ref AS credit_ref,
                    dm.move_type AS debit_move_type,
                    cm.move_type AS credit_move_type,
                    dm.date AS debit_move_date,
                    cm.date AS credit_move_date,
                    dm.invoice_date AS debit_invoice_date,
                    cm.invoice_date AS credit_invoice_date,
                    dm.invoice_date_due AS debit_due_date,
                    cm.invoice_date_due AS credit_due_date,
                    dm.partner_id AS debit_partner_id,
                    cm.partner_id AS credit_partner_id,
                    dm.invoice_user_id AS debit_salesperson_id,
                    cm.invoice_user_id AS credit_salesperson_id,
                    dm.company_id AS debit_company_id,
                    cm.company_id AS credit_company_id,
                    dm.currency_id AS debit_move_currency_id,
                    cm.currency_id AS credit_move_currency_id,
                    dm.amount_total AS debit_amount_total,
                    cm.amount_total AS credit_amount_total,
                    dm.amount_residual AS debit_amount_residual,
                    cm.amount_residual AS credit_amount_residual,
                    dm.state AS debit_state,
                    cm.state AS credit_state,
                    dm.payment_state AS debit_payment_state,
                    cm.payment_state AS credit_payment_state,
                    dm.journal_id AS debit_journal_id,
                    cm.journal_id AS credit_journal_id,
                    apd.id AS debit_payment_id,
                    apc.id AS credit_payment_id,
                    COALESCE(apd.date, dm.date) AS debit_payment_date,
                    COALESCE(apc.date, cm.date) AS credit_payment_date
                FROM account_partial_reconcile apr
                JOIN account_move_line dml
                    ON dml.id = apr.debit_move_id
                JOIN account_move_line cml
                    ON cml.id = apr.credit_move_id
                JOIN account_move dm
                    ON dm.id = dml.move_id
                JOIN account_move cm
                    ON cm.id = cml.move_id
                LEFT JOIN account_payment apd
                    ON apd.move_id = dm.id
                LEFT JOIN account_payment apc
                    ON apc.move_id = cm.id
                WHERE (
                    dm.move_type IN ('out_invoice', 'out_refund', 'out_receipt')
                    OR cm.move_type IN ('out_invoice', 'out_refund', 'out_receipt')
                )
                    -- Exclude pure internal / journal entry pairs with no customer side.
                    -- 'entry' moves are only included when the other side is a real
                    -- customer document (already covered by the OR above).
                    AND NOT (
                        dm.move_type = 'entry'
                        AND cm.move_type = 'entry'
                    )
            ),
            normalized AS (
                SELECT
                    rb.partial_reconcile_id,
                    rb.reconciliation_date,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_move_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_move_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_move_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_move_id
                    END AS invoice_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_move_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_move_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_move_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_move_id
                    END AS settlement_move_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_line_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_line_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_line_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_line_id
                    END AS invoice_move_line_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_line_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_line_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_line_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_line_id
                    END AS settlement_move_line_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_move_name
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_move_name
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_move_name
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_move_name
                    END AS invoice_name,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_move_name
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_move_name
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_move_name
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_move_name
                    END AS payment_name,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_partner_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_partner_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_partner_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_partner_id
                    END AS partner_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_salesperson_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_salesperson_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_salesperson_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_salesperson_id
                    END AS salesperson_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_company_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_company_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_company_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_company_id
                    END AS company_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_journal_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_journal_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_journal_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_journal_id
                    END AS journal_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_move_currency_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_move_currency_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_move_currency_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_move_currency_id
                    END AS currency_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_amount_total
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_amount_total
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_amount_total
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_amount_total
                    END AS invoice_total,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_amount_residual
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_amount_residual
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_amount_residual
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_amount_residual
                    END AS residual_amount,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_invoice_date
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_invoice_date
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_invoice_date
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_invoice_date
                    END AS invoice_date,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_due_date
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_due_date
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_due_date
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_due_date
                    END AS due_date,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_state
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_state
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_state
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_state
                    END AS invoice_state,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_payment_state
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_payment_state
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_payment_state
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_payment_state
                    END AS payment_state,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_payment_id
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_payment_id
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_payment_id
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_payment_id
                    END AS payment_id,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt') THEN rb.credit_payment_date
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt') THEN rb.debit_payment_date
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.credit_payment_date
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN rb.debit_payment_date
                    END AS payment_date,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt')
                            AND rb.debit_currency_id IS NOT NULL
                            AND COALESCE(rb.debit_amount_currency, 0) != 0
                            THEN ABS(rb.debit_amount_currency)
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt')
                            AND rb.credit_currency_id IS NOT NULL
                            AND COALESCE(rb.credit_amount_currency, 0) != 0
                            THEN ABS(rb.credit_amount_currency)
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            AND rb.debit_currency_id IS NOT NULL
                            AND COALESCE(rb.debit_amount_currency, 0) != 0
                            THEN ABS(rb.debit_amount_currency)
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            AND rb.credit_currency_id IS NOT NULL
                            AND COALESCE(rb.credit_amount_currency, 0) != 0
                            THEN ABS(rb.credit_amount_currency)
                        ELSE ABS(rb.company_amount)
                    END AS collected_amount,
                    CASE
                        WHEN rb.debit_move_type IN ('out_invoice', 'out_receipt')
                            THEN COALESCE(rb.credit_ref, rb.credit_move_name)
                        WHEN rb.credit_move_type IN ('out_invoice', 'out_receipt')
                            THEN COALESCE(rb.debit_ref, rb.debit_move_name)
                        WHEN rb.debit_move_type = 'out_refund'
                            AND rb.credit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN COALESCE(rb.credit_ref, rb.credit_move_name)
                        WHEN rb.credit_move_type = 'out_refund'
                            AND rb.debit_move_type NOT IN ('out_invoice', 'out_receipt')
                            THEN COALESCE(rb.debit_ref, rb.debit_move_name)
                    END AS memo
                FROM reconcile_base rb
            ),
            final_allocations AS (
                SELECT
                    n.*,
                    COUNT(*) OVER (
                        PARTITION BY n.invoice_id, n.settlement_move_id
                    ) AS allocation_count
                FROM normalized n
                WHERE n.invoice_id IS NOT NULL
                    AND n.settlement_move_id IS NOT NULL
                    AND n.invoice_id != n.settlement_move_id
            )
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY fa.payment_date DESC NULLS LAST, fa.partial_reconcile_id DESC
                ) AS id,
                fa.payment_date,
                fa.payment_id,
                fa.payment_name,
                fa.invoice_id,
                fa.invoice_name,
                fa.partner_id,
                fa.salesperson_id,
                fa.company_id,
                fa.journal_id,
                fa.currency_id,
                fa.collected_amount,
                fa.invoice_total,
                fa.residual_amount,
                fa.invoice_date,
                fa.due_date,
                CASE
                    WHEN fa.payment_date IS NOT NULL
                        AND fa.due_date IS NOT NULL
                        THEN GREATEST((fa.payment_date - fa.due_date), 0)
                    ELSE 0
                END AS payment_delay_days,
                fa.allocation_count,
                fa.invoice_state,
                fa.payment_state,
                fa.settlement_move_line_id AS reconciled_line_id,
                fa.settlement_move_line_id AS payment_move_line_id,
                fa.invoice_move_line_id,
                pd.product_names,
                fa.memo
            FROM final_allocations fa
            LEFT JOIN product_data pd
                ON pd.invoice_id = fa.invoice_id
        """

    def init(self):
        relation_name = self._table
        materialized = self._is_materialized_view_enabled()

        def _build_relation():
            self._drop_relation(relation_name)
            if materialized:
                self._create_materialized_view(relation_name, self._get_report_select_sql())
                self.env.cr.execute(
                    sql.SQL("CREATE UNIQUE INDEX IF NOT EXISTS {} ON {} (id)").format(
                        sql.Identifier(f"{relation_name}_id_uniq"),
                        sql.Identifier(relation_name),
                    )
                )
                self.env.cr.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} (company_id, payment_date DESC)").format(
                        sql.Identifier(f"{relation_name}_company_payment_date_idx"),
                        sql.Identifier(relation_name),
                    )
                )
                self.env.cr.execute(
                    sql.SQL("CREATE INDEX IF NOT EXISTS {} ON {} (invoice_id, partner_id, company_id)").format(
                        sql.Identifier(f"{relation_name}_invoice_partner_company_idx"),
                        sql.Identifier(relation_name),
                    )
                )
            else:
                self._create_standard_view(relation_name, self._get_report_select_sql())

        mode = "materialized_view" if materialized else "view"
        self._time_sql("collection_report_build", _build_relation, mode=mode, table=relation_name)

    @api.model
    def _create_refresh_history(self, status, mode, started_at, company_id=False, **extra):
        values = {
            "name": fields.Datetime.now(),
            "relation_name": self._table,
            "company_id": company_id or self.env.company.id,
            "status": status,
            "refresh_mode": mode,
            "started_at": started_at,
            **extra,
        }
        return self.env["collection.reconciliation.refresh.history"].sudo().create(values)

    @api.model
    def refresh_materialized_view(self, concurrently=True):
        if not self._is_materialized_view_enabled():
            self._log_structured("info", "collection_report_refresh_skipped", reason="feature_disabled")
            return False

        lock_key = self._get_refresh_lock_key(self._table)
        self.env.cr.execute("SELECT pg_try_advisory_lock(%s)", [lock_key])
        locked = self.env.cr.fetchone()[0]
        if not locked:
            self._create_refresh_history(
                "skipped",
                "concurrent" if concurrently else "standard",
                fields.Datetime.now(),
                error_message=_("Refresh skipped because another refresh is already running."),
            )
            self._log_structured("warning", "collection_report_refresh_skipped", reason="lock_busy")
            return False

        started_at = fields.Datetime.now()
        history = self._create_refresh_history(
            "running",
            "concurrent" if concurrently else "standard",
            started_at,
        )
        self.env.cr.commit()
        started_perf = time.perf_counter()
        statements = []
        if concurrently:
            statements.append(("concurrent", f"REFRESH MATERIALIZED VIEW CONCURRENTLY {self._table}"))
        statements.append(("standard", f"REFRESH MATERIALIZED VIEW {self._table}"))
        try:
            for mode, statement in statements:
                try:
                    if mode == "concurrent":
                        self.env.cr.commit()
                    self.env.cr.execute(statement)
                    self.env.cr.commit()
                    duration = time.perf_counter() - started_perf
                    history.write(
                        {
                            "status": "success",
                            "refresh_mode": mode,
                            "finished_at": fields.Datetime.now(),
                            "duration_seconds": duration,
                            "last_refresh_at": fields.Datetime.now(),
                        }
                    )
                    self.env.cr.commit()
                    self._log_structured(
                        "info",
                        "collection_report_refresh_success",
                        mode=mode,
                        duration_seconds=f"{duration:.3f}",
                    )
                    return True
                except Exception as exc:
                    self.env.cr.rollback()
                    history = self.env["collection.reconciliation.refresh.history"].sudo().browse(history.id)
                    self._log_structured(
                        "warning",
                        "collection_report_refresh_retry",
                        mode=mode,
                        error=str(exc),
                    )
                    history.write({"error_message": str(exc)})
                    self.env.cr.commit()
            duration = time.perf_counter() - started_perf
            history.write(
                {
                    "status": "failed",
                    "finished_at": fields.Datetime.now(),
                    "duration_seconds": duration,
                }
            )
            self.env.cr.commit()
            return False
        finally:
            self.env.cr.execute("SELECT pg_advisory_unlock(%s)", [lock_key])

    def action_refresh_materialized_view(self):
        success = self.refresh_materialized_view(concurrently=True)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Collection Report"),
                "message": _("Materialized analytics refresh completed.") if success else _("Refresh was skipped or failed. See refresh history for details."),
                "type": "success" if success else "warning",
                "sticky": not success,
            },
        }

    @api.model
    def cron_refresh_materialized_view(self):
        self.refresh_materialized_view(concurrently=True)
        return True

    @api.model
    def action_open_refresh_history(self):
        return self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_refresh_history"
        ).read()[0]

    @api.model
    def _load_demo_data_hook(self):
        """Called by demo/demo_data.xml via <function> tag.

        Delegates to the demo module so the main model file stays clean.
        Silently skips if demo data was already loaded (idempotent).
        """
        already_loaded = self.env["res.partner"].search_count(
            [("ref", "=like", "DEMO-CRR-%")]
        )
        if already_loaded:
            _logger.info(
                "collection_reconciliation_report: demo data already present — skipping."
            )
            return True
        try:
            from odoo.addons.collection_reconciliation_report.demo.demo_data import (
                load_demo_data,
            )
            load_demo_data(self.env)
        except Exception as exc:
            _logger.warning(
                "collection_reconciliation_report: demo data load failed — %s", exc
            )
        return True

    def action_open_invoice(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Invoice"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.invoice_id.id,
            "target": "current",
        }

    def action_open_payment(self):
        self.ensure_one()
        model = "account.payment" if self.payment_id else "account.move"
        res_id = self.payment_id.id or self.payment_move_line_id.move_id.id
        return {
            "type": "ir.actions.act_window",
            "name": _("Payment"),
            "res_model": model,
            "view_mode": "form",
            "res_id": res_id,
            "target": "current",
        }


class CollectionReconciliationReportKpi(models.Model):
    """Advanced SQL KPI dashboard for collection reconciliation."""

    _name = "collection.reconciliation.report.kpi"
    _description = "Collection Reconciliation Dashboard"
    _inherit = "collection.reconciliation.sql.mixin"
    _auto = False
    _order = "company_id, currency_id"

    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    currency_id = fields.Many2one("res.currency", string="Currency", readonly=True)
    total_collected = fields.Monetary(string="Total Collected", readonly=True)
    total_residual = fields.Monetary(string="Total Residual", readonly=True)
    total_invoice_amount = fields.Monetary(string="Total Invoice Amount", readonly=True)
    line_count = fields.Integer(string="Reconciliation Rows", readonly=True)
    invoice_count = fields.Integer(string="Invoices", readonly=True)
    payment_count = fields.Integer(string="Payments", readonly=True)
    customer_count = fields.Integer(string="Customers", readonly=True)
    partial_line_count = fields.Integer(string="Partial Rows", readonly=True)
    monthly_collection_growth = fields.Float(string="Monthly Growth %", readonly=True)
    collection_efficiency = fields.Float(string="Collection Efficiency %", readonly=True)
    recovery_ratio = fields.Float(string="Recovery Ratio %", readonly=True)
    average_payment_delay = fields.Float(string="Average Delay Days", readonly=True)
    overdue_exposure = fields.Monetary(string="Overdue Exposure", readonly=True)
    unpaid_invoice_ratio = fields.Float(string="Unpaid Invoice Ratio %", readonly=True)
    best_salesperson_id = fields.Many2one("res.users", string="Top Collector", readonly=True)
    best_salesperson_amount = fields.Monetary(string="Top Collector Amount", readonly=True)
    top_collectors = fields.Char(string="Top Collectors", readonly=True)
    last_refresh_at = fields.Datetime(string="Last Refresh", readonly=True)
    refresh_status = fields.Selection(
        [
            ("success", "Success"),
            ("failed", "Failed"),
            ("skipped", "Skipped"),
            ("running", "Running"),
            ("never", "Never Refreshed"),
        ],
        string="Refresh Status",
        readonly=True,
    )
    refresh_duration_seconds = fields.Float(string="Refresh Duration", readonly=True)
    is_stale = fields.Boolean(string="Stale Data", readonly=True)

    # ---------------------------------------------------------------------------
    # KPI SQL is split into a static template + a bound parameter tuple so the
    # stale_hours threshold — read from ir.config_parameter — is NEVER
    # interpolated into the SQL string.  Callers receive (sql, params) and must
    # pass params to cr.execute().  The int clamp is a defence-in-depth guard;
    # the real protection is the bind parameter.
    # ---------------------------------------------------------------------------

    @api.model
    def _get_kpi_select_sql(self):
        """Return (sql_string, params_tuple) for the KPI view query.

        Uses a bind parameter for stale_hours — never an f-string — so the
        query is injection-safe regardless of what is stored in ir.config_parameter.
        """
        stale_hours = self._get_int_param("collection_report.stale_after_hours", default=24)
        # Hard clamp: positive integer, 1 h – 1 year.
        stale_hours = max(1, min(int(stale_hours), 8760))
        sql = """
            WITH base AS (
                SELECT *
                FROM collection_reconciliation_report
            ),
            invoice_stats AS (
                SELECT
                    company_id,
                    currency_id,
                    COUNT(DISTINCT invoice_id) AS invoice_count,
                    COUNT(DISTINCT payment_id) AS payment_count,
                    COUNT(DISTINCT partner_id) AS customer_count,
                    SUM(collected_amount) AS total_collected,
                    SUM(residual_amount) AS total_residual,
                    SUM(invoice_total) AS total_invoice_amount,
                    COUNT(*) AS line_count,
                    COUNT(*) FILTER (WHERE ABS(collected_amount) < ABS(invoice_total)) AS partial_line_count,
                    AVG(payment_delay_days::numeric) AS average_payment_delay,
                    SUM(CASE WHEN due_date < CURRENT_DATE AND residual_amount > 0 THEN residual_amount ELSE 0 END) AS overdue_exposure,
                    CASE
                        WHEN COUNT(DISTINCT invoice_id) = 0 THEN 0
                        ELSE COUNT(DISTINCT invoice_id) FILTER (WHERE residual_amount > 0)::numeric
                            / COUNT(DISTINCT invoice_id)::numeric * 100
                    END AS unpaid_invoice_ratio
                FROM base
                GROUP BY company_id, currency_id
            ),
            monthly AS (
                SELECT
                    company_id,
                    currency_id,
                    DATE_TRUNC('month', payment_date) AS payment_month,
                    SUM(collected_amount) AS month_amount
                FROM base
                WHERE payment_date IS NOT NULL
                GROUP BY company_id, currency_id, DATE_TRUNC('month', payment_date)
            ),
            latest_months AS (
                SELECT
                    company_id,
                    currency_id,
                    month_amount,
                    LAG(month_amount) OVER (
                        PARTITION BY company_id, currency_id
                        ORDER BY payment_month
                    ) AS previous_month_amount,
                    ROW_NUMBER() OVER (
                        PARTITION BY company_id, currency_id
                        ORDER BY payment_month DESC
                    ) AS rownum
                FROM monthly
            ),
            salespeople AS (
                SELECT
                    company_id,
                    currency_id,
                    salesperson_id,
                    SUM(collected_amount) AS collected_amount
                FROM base
                WHERE salesperson_id IS NOT NULL
                GROUP BY company_id, currency_id, salesperson_id
            ),
            ranked_salespeople AS (
                SELECT
                    s.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.company_id, s.currency_id
                        ORDER BY s.collected_amount DESC, s.salesperson_id
                    ) AS rownum
                FROM salespeople s
            ),
            collector_labels AS (
                SELECT
                    rs.company_id,
                    rs.currency_id,
                    STRING_AGG(
                        rp.name || ' (' || TRIM(TO_CHAR(rs.collected_amount, 'FM9999999990.00')) || ')',
                        ', ' ORDER BY rs.collected_amount DESC
                    ) AS top_collectors
                FROM ranked_salespeople rs
                JOIN res_users ru
                    ON ru.id = rs.salesperson_id
                JOIN res_partner rp
                    ON rp.id = ru.partner_id
                WHERE rs.rownum <= 3
                GROUP BY rs.company_id, rs.currency_id
            ),
            latest_refresh AS (
                SELECT
                    h.company_id,
                    h.status,
                    h.last_refresh_at,
                    h.duration_seconds,
                    ROW_NUMBER() OVER (
                        PARTITION BY h.company_id
                        ORDER BY COALESCE(h.last_refresh_at, h.finished_at, h.started_at) DESC, h.id DESC
                    ) AS rownum
                FROM collection_reconciliation_refresh_history h
            )
            SELECT
                ROW_NUMBER() OVER (ORDER BY stat.company_id, stat.currency_id) AS id,
                stat.company_id,
                stat.currency_id,
                stat.total_collected,
                stat.total_residual,
                stat.total_invoice_amount,
                stat.line_count,
                stat.invoice_count,
                stat.payment_count,
                stat.customer_count,
                stat.partial_line_count,
                COALESCE(
                    CASE
                        WHEN lm.previous_month_amount IS NULL OR lm.previous_month_amount = 0 THEN 0
                        ELSE (lm.month_amount - lm.previous_month_amount) / lm.previous_month_amount * 100
                    END,
                    0
                ) AS monthly_collection_growth,
                CASE
                    WHEN stat.total_invoice_amount = 0 THEN 0
                    ELSE stat.total_collected / stat.total_invoice_amount * 100
                END AS collection_efficiency,
                CASE
                    WHEN (stat.total_collected + stat.total_residual) = 0 THEN 0
                    ELSE stat.total_collected / (stat.total_collected + stat.total_residual) * 100
                END AS recovery_ratio,
                COALESCE(stat.average_payment_delay, 0) AS average_payment_delay,
                stat.overdue_exposure,
                stat.unpaid_invoice_ratio,
                rs.salesperson_id AS best_salesperson_id,
                COALESCE(rs.collected_amount, 0) AS best_salesperson_amount,
                cl.top_collectors,
                lr.last_refresh_at,
                COALESCE(lr.status, 'never') AS refresh_status,
                COALESCE(lr.duration_seconds, 0) AS refresh_duration_seconds,
                CASE
                    WHEN lr.last_refresh_at IS NULL THEN TRUE
                    WHEN lr.last_refresh_at < (NOW() - (%s * INTERVAL '1 hour')) THEN TRUE
                    ELSE FALSE
                END AS is_stale
            FROM invoice_stats stat
            LEFT JOIN latest_months lm
                ON lm.company_id = stat.company_id
                AND lm.currency_id = stat.currency_id
                AND lm.rownum = 1
            LEFT JOIN ranked_salespeople rs
                ON rs.company_id = stat.company_id
                AND rs.currency_id = stat.currency_id
                AND rs.rownum = 1
            LEFT JOIN collector_labels cl
                ON cl.company_id = stat.company_id
                AND cl.currency_id = stat.currency_id
            LEFT JOIN latest_refresh lr
                ON lr.company_id = stat.company_id
                AND lr.rownum = 1
        """
        return sql, (stale_hours,)

    def init(self):
        # Ensure the refresh history table exists before building the KPI view.
        # The KPI SQL references collection_reconciliation_refresh_history and
        # PostgreSQL resolves table names at parse time, so the table must exist
        # even if empty when the view is first created.
        self.env.cr.execute("""
            CREATE TABLE IF NOT EXISTS collection_reconciliation_refresh_history (
                id                  SERIAL PRIMARY KEY,
                name                TIMESTAMP WITH TIME ZONE,
                relation_name       VARCHAR,
                company_id          INTEGER,
                status              VARCHAR,
                refresh_mode        VARCHAR,
                started_at          TIMESTAMP WITH TIME ZONE,
                finished_at         TIMESTAMP WITH TIME ZONE,
                last_refresh_at     TIMESTAMP WITH TIME ZONE,
                duration_seconds    NUMERIC,
                error_message       TEXT
            )
        """)
        kpi_sql, kpi_params = self._get_kpi_select_sql()

        def _build():
            self._drop_relation(self._table)
            self._create_standard_view(self._table, kpi_sql, params=list(kpi_params))

        self._time_sql(
            "collection_kpi_build",
            _build,
            table=self._table,
        )

    def action_open_lines(self):
        self.ensure_one()
        action = self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_report"
        ).read()[0]
        action["domain"] = [
            ("company_id", "=", self.company_id.id),
            ("currency_id", "=", self.currency_id.id),
        ]
        return action

    def action_open_refresh_history(self):
        return self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_refresh_history"
        ).read()[0]

    def action_refresh_dashboard(self):
        self.env["collection.reconciliation.report"].refresh_materialized_view(concurrently=True)
        return self.env.ref(
            "collection_reconciliation_report.action_collection_reconciliation_report_dashboard"
        ).read()[0]


class CollectionReconciliationRefreshHistory(models.Model):
    """Audit trail and monitoring for materialized view refreshes."""

    _name = "collection.reconciliation.refresh.history"
    _description = "Collection Reconciliation Refresh History"
    _order = "started_at desc, id desc"

    name = fields.Datetime(string="Refresh Reference", required=True, readonly=True)
    relation_name = fields.Char(string="Relation", required=True, readonly=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=True)
    status = fields.Selection(
        [
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("skipped", "Skipped"),
        ],
        string="Status",
        required=True,
        readonly=True,
    )
    refresh_mode = fields.Selection(
        [
            ("concurrent", "Concurrent"),
            ("standard", "Standard"),
        ],
        string="Refresh Mode",
        readonly=True,
    )
    started_at = fields.Datetime(string="Started At", readonly=True)
    finished_at = fields.Datetime(string="Finished At", readonly=True)
    last_refresh_at = fields.Datetime(string="Last Refresh", readonly=True)
    duration_seconds = fields.Float(string="Duration (s)", readonly=True)
    error_message = fields.Text(string="Error", readonly=True)
