"""
Collection Reconciliation Report — Demo Data
=============================================
Creates a realistic set of customers, invoices, payments, and reconciliations
so the report and KPI dashboard show meaningful data immediately after install.

Scenarios covered
-----------------
  1. Fully paid on time          → payment_state = 'paid',  delay = 0
  2. Fully paid late             → payment_state = 'paid',  delay > 0
  3. Partially paid              → payment_state = 'partial'
  4. Overdue — unpaid residual   → due_date in the past, residual > 0
  5. Multi-payment allocation    → one invoice settled by two separate payments
  6. Credit note offset          → out_refund reconciled against an invoice

All amounts are in the company currency.  The data spans the last 12 months
so the KPI "monthly growth" calculation has enough history to produce a
non-zero trend.
"""

import logging
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _months_ago(n):
    return date.today() - relativedelta(months=n)

def _days_ago(n):
    return date.today() - timedelta(days=n)


def _get_or_create_product(env, name, price):
    Product = env["product.product"]
    existing = Product.search([("name", "=", name)], limit=1)
    if existing:
        return existing
    return Product.create({
        "name": name,
        "type": "service",
        "list_price": price,
        "categ_id": env.ref("product.product_category_all").id,
    })


def _get_or_create_partner(env, name, ref):
    Partner = env["res.partner"]
    existing = Partner.search([("ref", "=", ref), ("customer_rank", ">", 0)], limit=1)
    if existing:
        return existing
    return Partner.create({
        "name": name,
        "ref": ref,
        "customer_rank": 1,
        "company_type": "company",
        "country_id": env.ref("base.eg").id,
    })


def _get_customer_journal(env):
    journal = env["account.journal"].search(
        [("type", "=", "bank"), ("company_id", "=", env.company.id)],
        limit=1,
    )
    if not journal:
        journal = env["account.journal"].search(
            [("type", "=", "cash"), ("company_id", "=", env.company.id)],
            limit=1,
        )
    return journal


def _get_receivable_account(env):
    """Return the default receivable account for the current company."""
    return env["account.account"].search(
        [
            ("account_type", "=", "asset_receivable"),
            ("company_id", "=", env.company.id),
            ("deprecated", "=", False),
        ],
        limit=1,
    )


def _get_income_account(env):
    return env["account.account"].search(
        [
            ("account_type", "=", "income"),
            ("company_id", "=", env.company.id),
            ("deprecated", "=", False),
        ],
        limit=1,
    )


def _create_invoice(env, partner, product, amount, invoice_date, due_date, salesperson=None):
    """Create and post a customer invoice. Returns the posted account.move."""
    income_account = _get_income_account(env)
    vals = {
        "move_type": "out_invoice",
        "partner_id": partner.id,
        "invoice_date": invoice_date,
        "invoice_date_due": due_date,
        "invoice_line_ids": [(0, 0, {
            "product_id": product.id,
            "name": product.name,
            "quantity": 1,
            "price_unit": amount,
            "account_id": income_account.id,
        })],
    }
    if salesperson:
        vals["invoice_user_id"] = salesperson.id
    invoice = env["account.move"].create(vals)
    invoice.action_post()
    return invoice


def _create_payment_and_reconcile(env, invoice, amount, payment_date, journal):
    """Register a payment and reconcile it against the invoice."""
    payment_vals = {
        "payment_type": "inbound",
        "partner_type": "customer",
        "partner_id": invoice.partner_id.id,
        "amount": amount,
        "date": payment_date,
        "journal_id": journal.id,
        "currency_id": invoice.currency_id.id,
        "ref": f"PMT/{invoice.name}",
    }
    payment = env["account.payment"].create(payment_vals)
    payment.action_post()

    # Reconcile the payment move line against the invoice move line.
    receivable_lines = invoice.line_ids.filtered(
        lambda l: l.account_id.account_type == "asset_receivable"
    )
    payment_lines = payment.move_id.line_ids.filtered(
        lambda l: l.account_id.account_type == "asset_receivable"
    )
    if receivable_lines and payment_lines:
        (receivable_lines + payment_lines).reconcile()

    return payment


def _create_credit_note_and_reconcile(env, invoice, amount, cn_date):
    """Create a credit note and reconcile it against the invoice."""
    income_account = _get_income_account(env)
    cn = env["account.move"].create({
        "move_type": "out_refund",
        "partner_id": invoice.partner_id.id,
        "invoice_date": cn_date,
        "invoice_date_due": cn_date,
        "invoice_line_ids": [(0, 0, {
            "product_id": invoice.invoice_line_ids[0].product_id.id,
            "name": "Credit Note — partial return",
            "quantity": 1,
            "price_unit": amount,
            "account_id": income_account.id,
        })],
        "ref": f"CN/{invoice.name}",
    })
    cn.action_post()

    inv_lines = invoice.line_ids.filtered(
        lambda l: l.account_id.account_type == "asset_receivable"
    )
    cn_lines = cn.line_ids.filtered(
        lambda l: l.account_id.account_type == "asset_receivable"
    )
    if inv_lines and cn_lines:
        (inv_lines + cn_lines).reconcile()

    return cn


# ---------------------------------------------------------------------------
# Main entry point called by Odoo's demo data loader
# ---------------------------------------------------------------------------

def load_demo_data(env):
    _logger.info("collection_reconciliation_report: loading demo data …")

    company = env.company
    journal = _get_customer_journal(env)
    if not journal:
        _logger.warning(
            "collection_reconciliation_report: no bank/cash journal found — "
            "skipping demo data."
        )
        return

    # ── Products ──────────────────────────────────────────────────────────
    p_consulting  = _get_or_create_product(env, "Consulting Services",   5_000.0)
    p_support     = _get_or_create_product(env, "Annual Support Plan",   2_400.0)
    p_license     = _get_or_create_product(env, "Software License",      8_500.0)
    p_training    = _get_or_create_product(env, "Training Workshop",     1_200.0)
    p_integration = _get_or_create_product(env, "Integration Services", 12_000.0)

    # ── Partners ──────────────────────────────────────────────────────────
    alpha   = _get_or_create_partner(env, "Alpha Industries",      "DEMO-CRR-001")
    beta    = _get_or_create_partner(env, "Beta Solutions Ltd",    "DEMO-CRR-002")
    gamma   = _get_or_create_partner(env, "Gamma Trading Co",      "DEMO-CRR-003")
    delta   = _get_or_create_partner(env, "Delta Enterprises",     "DEMO-CRR-004")
    epsilon = _get_or_create_partner(env, "Epsilon Tech Group",    "DEMO-CRR-005")
    zeta    = _get_or_create_partner(env, "Zeta Financial Services","DEMO-CRR-006")

    # ── Salespersons (use admin + portal user if available) ────────────────
    salesperson_a = env.ref("base.user_admin", raise_if_not_found=False)
    salesperson_b = env["res.users"].search(
        [("share", "=", False), ("id", "!=", salesperson_a.id)], limit=1
    ) or salesperson_a

    # ======================================================================
    # SCENARIO 1 — Fully paid on time (6 invoices across last 6 months)
    # ======================================================================
    for i, (partner, product, amount, months_back) in enumerate([
        (alpha,   p_consulting,  5_000.0, 6),
        (alpha,   p_support,     2_400.0, 5),
        (beta,    p_license,     8_500.0, 4),
        (beta,    p_consulting,  5_000.0, 3),
        (gamma,   p_integration,12_000.0, 2),
        (epsilon, p_training,    1_200.0, 1),
    ]):
        inv_date = _months_ago(months_back)
        due_date = inv_date + timedelta(days=30)
        # Paid 5–10 days before due
        pay_date = due_date - timedelta(days=5 + i)
        sp = salesperson_a if i % 2 == 0 else salesperson_b
        inv = _create_invoice(env, partner, product, amount, inv_date, due_date, sp)
        _create_payment_and_reconcile(env, inv, amount, pay_date, journal)

    # ======================================================================
    # SCENARIO 2 — Fully paid late (creates payment_delay_days > 0)
    # ======================================================================
    for partner, product, amount, months_back, delay in [
        (gamma,   p_consulting,  7_500.0, 5, 15),
        (delta,   p_support,     2_400.0, 4, 22),
        (zeta,    p_license,     8_500.0, 3, 31),
        (epsilon, p_integration,12_000.0, 2, 45),
    ]:
        inv_date = _months_ago(months_back)
        due_date = inv_date + timedelta(days=30)
        pay_date = due_date + timedelta(days=delay)
        inv = _create_invoice(env, partner, product, amount, inv_date, due_date, salesperson_b)
        _create_payment_and_reconcile(env, inv, amount, pay_date, journal)

    # ======================================================================
    # SCENARIO 3 — Partially paid (payment_state = 'partial')
    # ======================================================================
    for partner, product, amount, paid_amount, months_back in [
        (alpha,   p_integration, 12_000.0,  8_000.0, 2),
        (beta,    p_consulting,   5_000.0,  3_000.0, 1),
        (delta,   p_license,      8_500.0,  5_000.0, 1),
    ]:
        inv_date = _months_ago(months_back)
        due_date = inv_date + timedelta(days=30)
        pay_date = inv_date + timedelta(days=20)
        inv = _create_invoice(env, partner, product, amount, inv_date, due_date, salesperson_a)
        _create_payment_and_reconcile(env, inv, paid_amount, pay_date, journal)

    # ======================================================================
    # SCENARIO 4 — Overdue unpaid (due_date in the past, no payment)
    # ======================================================================
    for partner, product, amount, days_overdue in [
        (gamma,   p_support,      2_400.0, 45),
        (delta,   p_training,     1_200.0, 30),
        (zeta,    p_consulting,   5_000.0, 60),
        (epsilon, p_license,      8_500.0, 20),
    ]:
        inv_date = _days_ago(days_overdue + 30)
        due_date = _days_ago(days_overdue)
        _create_invoice(env, partner, product, amount, inv_date, due_date, salesperson_b)
    # Note: no payment → these appear in overdue_exposure KPI

    # ======================================================================
    # SCENARIO 5 — Multi-payment allocation (one invoice, two payments)
    # ======================================================================
    inv_date  = _months_ago(3)
    due_date  = inv_date + timedelta(days=30)
    big_inv   = _create_invoice(env, zeta, p_integration, 15_000.0, inv_date, due_date, salesperson_a)
    _create_payment_and_reconcile(env, big_inv,  8_000.0, inv_date + timedelta(days=10), journal)
    _create_payment_and_reconcile(env, big_inv,  7_000.0, inv_date + timedelta(days=25), journal)

    # ======================================================================
    # SCENARIO 6 — Credit note offset (out_refund reconciled with invoice)
    # ======================================================================
    inv_date = _months_ago(2)
    due_date = inv_date + timedelta(days=30)
    cn_inv   = _create_invoice(env, beta, p_consulting, 5_000.0, inv_date, due_date, salesperson_a)
    # Full payment first
    _create_payment_and_reconcile(env, cn_inv, 5_000.0, inv_date + timedelta(days=15), journal)
    # Then a partial credit note (return of services)
    _create_credit_note_and_reconcile(env, cn_inv, 1_500.0, inv_date + timedelta(days=20))

    _logger.info(
        "collection_reconciliation_report: demo data loaded — "
        "%d customers, mixed paid/partial/overdue/multi-payment/credit-note scenarios.",
        6,
    )
