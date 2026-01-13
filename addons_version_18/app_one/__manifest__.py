{
    'name': 'Property Management',
    'version': '18.0.1.0',
    'category': 'Industries',
    'summary': 'Manage Properties, Owners & Real Estate Workflow',
    'description': """
Property Management System
==========================
Features:
* Manage properties with full details
* Track property owners
* Property state workflow
* Tag system for categorization
* Chatter integration for communication
    """,
    'author': 'Haytham Gamal',
    'website': 'https://github.com/haytham/property-management',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'contacts',
        'mail',
        'web',
        'account',
        'sale',
        'sale_management',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',

        'views/property_view.xml',
        'views/owner_view.xml',
        'views/tag_view.xml',
        'views/sale_order_inheeirt_view.xml',
        'views/res_partner_inheeirt_view.xml',
        'views/building_view.xml',
        'views/property_history_view.xml',
        'views/account_move_views.xml',
        'views/base_menu_view.xml',
        'report/propert_report.xml',
        'wizard/property_wizard_view.xml',

    ],
    'images': ['static/description/icon.png'],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'app_one/static/src/css/property.css',
            'app_one/static/src/components/listView/listView.css',
            'app_one/static/src/components/listView/listView.js',
            'app_one/static/src/components/listView/listView.xml',
            'app_one/static/src/components/formView/formView.css',
            'app_one/static/src/components/formView/formView.js',
            'app_one/static/src/components/formView/formView.xml',
        ],
        'web.report_assets_common': [
            'app_one/static/src/css/font.css',
        ],

    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
