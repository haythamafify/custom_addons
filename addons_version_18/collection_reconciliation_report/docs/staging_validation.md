# Staging Validation Runbook

## Objective

This runbook provides the executable staging process for validating `collection_reconciliation_report` before production deployment.

## Stage 1: Environment Parity

Confirm the staging environment matches production for:

- Odoo version
- PostgreSQL major version
- addons path ordering
- installed dependencies
- company structure
- currencies
- accounting journals

## Stage 2: Backup and Restore Validation

Create a restore point before validation:

```bash
pg_dump -Fc -d <staging_db> -f staging_before_collection_reconciliation_report.dump
tar -czf staging_addons_snapshot.tgz /path/to/addons
```

## Stage 3: Fresh Install Validation

```bash
odoo-bin -d <fresh_db> -c <odoo.conf> --stop-after-init -i collection_reconciliation_report --log-level=info
```

Validation checklist:

- `[]` module installs without traceback
- `[]` report actions resolve
- `[]` menus appear
- `[]` smart buttons load
- `[]` cron exists
- `[]` SQL relation created successfully

## Stage 4: Upgrade Validation

```bash
odoo-bin -d <staging_db> -c <odoo.conf> --stop-after-init -u collection_reconciliation_report --log-level=info
```

Monitor logs:

```bash
tail -f /var/log/odoo/odoo.log | grep -E "collection_reconciliation_report|ERROR|CRITICAL|Traceback|WARNING"
```

Upgrade checks:

- `[]` no `External ID not found`
- `[]` no `Invalid field`
- `[]` no view inheritance conflict
- `[]` no SQL relation creation failure
- `[]` no report registration failure

## Stage 5: PostgreSQL Validation

```sql
SELECT relname, relkind
FROM pg_class
WHERE relname IN (
    'collection_reconciliation_report',
    'collection_reconciliation_report_kpi'
);
```

```sql
SELECT schemaname, indexname, indexdef
FROM pg_indexes
WHERE tablename = 'collection_reconciliation_report';
```

Checks:

- `[]` relation type matches configured mode
- `[]` required indexes exist in materialized mode
- `[]` refresh history table contains records after manual refresh

## Stage 6: Accounting QA Execution

Run the following scenarios on staging:

- customer invoice full payment
- partial payment
- one payment to many invoices
- many payments to one invoice
- credit note
- refund
- advance payment
- write-off
- multicurrency settlement
- multi-company visibility

For each scenario:

- validate Odoo accounting state
- validate analytics row output
- validate residual amount consistency

## Stage 7: UI and Export Validation

- `[]` tree view loads
- `[]` pivot view loads
- `[]` graph views render
- `[]` kanban dashboard loads
- `[]` search filters work
- `[]` smart buttons open correct domains
- `[]` XLSX export works for manager
- `[]` XLSX export hidden for non-manager

## Stage 8: Security Validation

Test with:

- analytics user
- analytics manager
- restricted-company user

Checks:

- `[]` line report respects company visibility
- `[]` dashboard restricted to manager
- `[]` refresh history restricted to manager
- `[]` refresh actions restricted to manager
- `[]` export restricted to manager

## Stage 9: Production Readiness Checklist

| Check | Status |
|---|---|
| Fresh install passed | `[] Pass` `[] Fail` |
| Upgrade passed | `[] Pass` `[] Fail` |
| PostgreSQL validation passed | `[] Pass` `[] Fail` |
| Accounting QA signed off | `[] Pass` `[] Fail` |
| Security validation passed | `[] Pass` `[] Fail` |
| UI validation passed | `[] Pass` `[] Fail` |
| XLSX validation passed | `[] Pass` `[] Fail` |
| Rollback procedure tested | `[] Pass` `[] Fail` |

## Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Release Engineer |  |  |  |
| ERP QA Lead |  |  |  |
| Accounting Lead |  |  |  |
| Database Owner |  |  |  |
