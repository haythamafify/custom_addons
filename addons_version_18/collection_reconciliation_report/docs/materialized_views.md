# Materialized Views

## Purpose

Materialized view mode is provided to support high-volume reporting workloads where read performance is prioritized over immediate real-time visibility.

## Refresh Lifecycle

1. Materialized mode is enabled through system settings.
2. Module upgrade rebuilds the reporting relation as a materialized view.
3. Refresh can be triggered:
- manually from the report UI
- manually from shell
- automatically through cron
4. Refresh history records:
- status
- mode
- timing
- error message
- last refresh timestamp

## Concurrent Refresh

The refresh engine attempts:

1. `REFRESH MATERIALIZED VIEW CONCURRENTLY`
2. fallback to standard refresh when concurrent refresh fails

Concurrent refresh prerequisites:

- materialized relation exists
- unique index on `id` exists
- PostgreSQL allows concurrent operation under current transaction state

## Advisory Locks

The module uses PostgreSQL advisory locking to avoid overlapping refresh operations across workers.

Operational effect:

- one refresh can run at a time for the relation
- overlapping attempts are skipped and logged
- refresh history records the skip outcome

## Stale Detection

KPI records expose stale-data status using:

- last refresh timestamp
- configured stale threshold in hours

If the last successful refresh is older than the configured threshold, the dashboard should be treated as stale for operational decision-making.

## Monitoring

### Refresh history query

```sql
SELECT company_id, status, refresh_mode, started_at, finished_at, duration_seconds, error_message
FROM collection_reconciliation_refresh_history
ORDER BY started_at DESC
LIMIT 20;
```

### Activity monitoring

```sql
SELECT pid, usename, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE query ILIKE '%collection_reconciliation_report%';
```

## Recovery

### Manual refresh

```bash
odoo-bin shell -d <db> -c <odoo.conf> <<'PY'
env['collection.reconciliation.report'].refresh_materialized_view(concurrently=True)
PY
```

### Rebuild after corruption

```sql
DROP MATERIALIZED VIEW IF EXISTS collection_reconciliation_report CASCADE;
```

Then:

```bash
odoo-bin -d <db> -c <odoo.conf> --stop-after-init -u collection_reconciliation_report
```

### Mode fallback

If refresh performance or operational safety is unacceptable:

- disable materialized mode
- rerun module upgrade
- operate in standard view mode
