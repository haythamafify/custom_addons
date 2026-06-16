# Accounting Flows

## Scope

This document explains how the module interprets real accounting reconciliation flows.

## Payment Allocation Flow

### Standard Customer Payment

1. Customer invoice is posted.
2. Customer payment is posted.
3. Receivable lines are reconciled.
4. `account_partial_reconcile` stores the settlement link.
5. The report produces one allocation line per reconcile slice.

Expected analytics behavior:

- `invoice_id` references the customer invoice
- `payment_id` references the payment when available
- `collected_amount` equals the exact settled amount only

## Partial Reconciliation Logic

For partial payment scenarios:

1. Invoice remains partially open.
2. One `account_partial_reconcile` row exists for the settled portion.
3. The report shows only the settled portion.
4. `residual_amount` mirrors the invoice residual from Odoo core.

Example:

- invoice total: `1000`
- payment: `400`
- collected amount in report: `400`
- residual in report: `600`

## One Payment to Many Invoices

When one payment is allocated across several invoices:

- multiple `account_partial_reconcile` rows are created
- the report produces one line per invoice allocation
- all rows share the same payment-side context

## Many Payments to One Invoice

When several payments settle one invoice:

- the report produces one line per payment allocation
- invoice residual decreases after each reconcile event
- final residual becomes zero once fully settled

## Refunds

Refund-linked settlements are recognized through reconciliation relationships, not through UI assumptions.

Expected behavior:

- refund allocation appears as a settlement slice
- no false duplication should occur unless multiple real reconcile rows exist

## Credit Notes

Credit notes reduce invoice exposure when reconciled.

Expected behavior:

- invoice remains the business target
- credit note acts as settlement-side reduction
- analytics line reflects the exact applied amount

## Advance Payments

Advance payments are not reported merely because they exist.

They appear only when:

- the advance is posted
- later reconciled against a target invoice

This ensures the report reflects allocation truth, not available credit balances.

## Write-Offs

When Odoo finalizes settlement with write-off logic:

- the report should reflect only the reconciled allocation slice
- write-off behavior must not inflate `collected_amount`
- final residual must stay consistent with the invoice in `account.move`

## Exchange Differences

In multicurrency reconciliation flows:

- Odoo may generate exchange difference entries
- the module still anchors on real reconciliation links
- collected amounts are derived with invoice/payment currency logic where available

Validation rule:

- no duplicate reporting rows unless distinct reconcile slices exist

## Vendor Bills

The module primarily targets collection analytics.

Vendor-side flows should be tested to confirm:

- no unintended customer analytics leakage
- no false allocation rows in customer-focused analytics output

## Validation Principle

For every scenario:

1. validate Odoo core accounting result first
2. validate analytics result second
3. accept analytics only when it matches reconciliation truth
