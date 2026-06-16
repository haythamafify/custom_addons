# Copyright 2026
# License OPL-1 (https://www.odoo.com/documentation/user/legal/licenses.html)
{
    "name": "Collection Reconciliation Report",
    "summary": "Enterprise collection allocation analytics with SQL, KPIs, XLSX, and materialized views",
    "version": "18.0.3.0.0",
    "category": "Accounting/Accounting",
    "author": "Haytham Afify",
    "maintainer": "Haytham Afify",
    "website": "https://github.com/haythamafify",
    "support": "haythamgamal6@gmail.com",
    "license": "OPL-1",
    "price": "79.00",
    "currency": "USD",
    "depends": ["account"],
    "auto_install": False,
    "images": [
        "static/description/banner.png",
        "static/description/icon.png",
    ],
    "data": [
        "security/collection_security.xml",
        "security/collection_record_rules.xml",
        "security/ir.model.access.csv",
        "data/collection_report_cron.xml",
        "views/collection_report_views.xml",
        "views/account_move_views.xml",
        "views/account_payment_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "application": False,
    "demo": [
        "demo/demo_data.xml",
    ],
}
