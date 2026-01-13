# -*- coding: utf-8 -*-
{
    'name': "test_pos_custom",

    'summary': "Custom POS enhancements for discount management and payment methods.",

    'description': """
This module provides custom functionality for the Point of Sale system, including:
- Discount management with password protection.
- Custom payment methods.
- Additional POS user permissions.
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Point Of Sale',
    'version': '0.1',

    # Dependencies for this module to work correctly
    'depends': ['base', 'point_of_sale'],

    # Always loaded data files
    'data': [
        'security/pos_group.xml',
        'views/views.xml',
        'views/pos_config_inheirt.xml',
        'views/templates.xml',
    ],

    # Define assets (JS, CSS, XML)
    'assets': {
        'point_of_sale.assets': [
            'test_pos_custom/static/src/js/add_payment_method.js',
            'test_pos_custom/static/src/js/discount_access.js',
            'test_pos_custom/static/src/js/pos_limit.js',
        ],
        'web.assets_backend': [],
        'web.assets_frontend': [],
        'web.report.assets_common': [],
    },

    # Demonstration mode data files
    'demo': [
        'demo/demo.xml',
    ],
}
