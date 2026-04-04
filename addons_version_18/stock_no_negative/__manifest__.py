# -*- coding: utf-8 -*-
{
    'name': 'Prevent Negative Stock',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Prevents stock moves that would result in negative inventory',
    'description': """
        Prevents validation of stock pickings/moves when the on-hand quantity
        in the source location is insufficient. Supports per-category override
        via the 'Allow Negative Stock' boolean on Product Category.
    """,
    'author': 'Custom',
    'depends': ['stock'],
    'data': [
        'views/product_category_views.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
