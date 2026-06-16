# Architecture

## Design Objective

`collection_reconciliation_report` is designed to provide allocation-level collection analytics using `account_partial_reconcile` as the source of truth.

The architecture is SQL-centric by design to avoid heavy ORM loops and computed accounting reconstructions.

## Reporting Architecture

### Layer 1: Reconciliation Source

The module anchors on:

- `account_partial_reconcile`

This ensures every analytics row corresponds to a real reconciliation slice rather than inferred payment behavior.

### Layer 2: Move-Line Resolution

Each partial reconciliation resolves:

- debit move line
- credit move line
- source moves
- payment metadata when available

This allows the engine to distinguish:

- invoice side
- settlement side
- payment-driven allocations
- credit/refund-driven allocations

### Layer 3: Normalized Allocation Model

The model `collection.reconciliation.report` normalizes the raw accounting relationship into:

- invoice
- payment or settlement move
- customer
- salesperson
- journal
- company
- currency
- collected amount
- residual amount

Each analytics line represents one actual allocation slice.

## SQL View Architecture

### `product_data`

Aggregates invoice product names using `STRING_AGG`.

### `reconcile_base`

Joins:

- `account_partial_reconcile`
- `account_move_line`
- `account_move`
- `account_payment`

This stage enriches raw reconciliation rows with accounting context.

### `normalized`

Resolves business meaning:

- which move is the invoice
- which move is the settlement side
- what amount represents the exact collected slice
- which partner and company own the allocation

### Final Allocation Stage

Adds:

- synthetic `id` using `ROW_NUMBER()`
- payment delay days
- allocation count
- product aggregation

## `account_partial_reconcile` Flow

```text
account_partial_reconcile
    -> debit move line
    -> credit move line
    -> debit move / credit move
    -> invoice-side resolution
    -> settlement-side resolution
    -> normalized collection allocation row
```

## Reconciliation Lifecycle

1. Accounting documents are posted.
2. Odoo creates reconciliation links in `account_partial_reconcile`.
3. The reporting SQL reads those links.
4. The line report exposes exact allocation rows.
5. The KPI layer aggregates line-level analytics.
6. Optional materialized mode accelerates high-volume reporting.

## KPI Engine

The KPI engine is implemented as a separate SQL-backed model:

- `collection.reconciliation.report.kpi`

It aggregates:

- collection totals
- residual exposure
- payment delays
- recovery ratio
- overdue exposure
- top collectors
- refresh-state metadata

## Materialized View Mode

When enabled through configuration:

- the line report relation is built as a PostgreSQL materialized view
- refresh is performed manually or by cron
- refresh history is stored for monitoring
- stale-data status is propagated to KPI outputs

## Administrative Architecture

Supporting administrative models and actions include:

- refresh history model
- system settings for materialized mode, debug logging, and stale thresholds
- cron-based refresh mechanism
- manager-only operational controls
