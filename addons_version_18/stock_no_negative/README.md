# stock_no_negative — Prevent Negative Stock (Odoo 18)

## Overview
This module blocks the final validation (`_action_done`) of any **outgoing** stock
move when the available quantity at the source (internal) location would drop below
zero. An Arabic `UserError` is raised listing every violating product, its
available quantity, and the demanded quantity.

---

## Features
| Feature | Details |
|---|---|
| **Validation hook** | Overrides `stock.move._action_done` |
| **Scope** | Only internal source locations (`location_id.usage == 'internal'`) |
| **Per-category bypass** | `product.category.allow_negative_stock` (Boolean, default `False`) |
| **Error language** | Arabic (`UserError`) |
| **Performance** | Single `stock.quant` query per picking; demand aggregated before comparison |
| **Multi-move safe** | All moves in one picking are aggregated per (location, product) |

---

## Installation
1. Copy the `stock_no_negative` folder into your Odoo `addons` path.
2. Restart the Odoo service.
3. Activate **Developer Mode** → Apps → Update App List.
4. Search for **"Prevent Negative Stock"** and install.

---

## Configuration

### Allow Negative Stock per Category
Go to **Inventory → Configuration → Product Categories** → open any category → tab **Logistics** → enable **Allow Negative Stock / السماح بالمخزون السالب**.

When enabled, products in that category will be allowed to go negative (no blocking).

---

## Technical Notes

### Files
```
stock_no_negative/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_category.py   # adds allow_negative_stock field
│   └── stock_move.py         # core prevention logic
├── views/
│   └── product_category_views.xml
└── i18n/
    └── ar.po
```

### Logic flow (`stock_move.py`)
```
_action_done()
  └── _check_negative_stock()
        ├── _get_moves_to_check()          — filter: internal src + categ not bypassed
        ├── aggregate demand per (loc, product)
        ├── _compute_location_product_qty()— single quant query
        └── compare → raise UserError (Arabic) if any product is short
```

### Error message example
```
لا يمكن إتمام العملية — الكمية غير كافية في المخزن للمنتجات التالية:

المنتج: Pain au chocolat croissant
الموقع: WH/Stock
الكمية المتاحة: 3.00 Units
الكمية المطلوبة: 5.00 Units
```

---

## Compatibility
- **Odoo**: 18.0
- **Dependencies**: `stock` (core)
