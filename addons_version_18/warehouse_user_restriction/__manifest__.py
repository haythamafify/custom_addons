{
    "name": "Warehouse User Restriction",
    "version": "18.0.1.0.0",
    "summary": "Restrict warehouse-related records per user using record rules",
    "description": """
Production-ready warehouse access restriction module for Odoo 18.
Users can access only assigned warehouses and related stock records.
    """,
    "category": "Inventory",
    "author": "Haytham Afify",
    "website": "https://github.com/haythamafify/custom_addons",
    "linkedin": "https://www.linkedin.com/in/haytham-gamal-4165797a/",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_users_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
