# Warehouse User Restriction (Odoo 18)

Restrict warehouse-related access per user using record rules.

## Features

- Add `Allowed Warehouses` on user form (`res.users`).
- Restrict visibility of:
  - Warehouses (`stock.warehouse`)
  - Pickings (`stock.picking`)
  - Quants (`stock.quant`)
  - Locations (`stock.location`)
- Company-aware filtering using `user.company_ids`.
- System administrators (`base.group_system`) are not restricted.

## Module Info

- Technical name: `warehouse_user_restriction`
- Version: `18.0.1.0.0`
- Depends on: `stock`
- License: `LGPL-3`

## Installation

1. Place this module in your Odoo addons path.
2. Update Apps list.
3. Install module `Warehouse User Restriction`.

## Configuration

1. Go to `Settings -> Users & Companies -> Users`.
2. Open a target user.
3. In **Warehouse Restrictions**, set **Allowed Warehouses**.
4. Save user, then logout/login as that user.

## Security Behavior

- Rules are defined in `security/security.xml`.
- For non-system users, access is limited to assigned warehouses and related location trees.
- For `base.group_system`, rules return full access (`[(1, '=', 1)]`).

## Notes

- If a user has no `Allowed Warehouses`, they will effectively see no restricted records.
- After any security rule change, upgrade the module and re-login the user.

## Files

- `models/res_users.py`: adds `warehouse_ids` field.
- `views/res_users_views.xml`: adds user form UI for allowed warehouses.
- `security/security.xml`: record rules and groups.

