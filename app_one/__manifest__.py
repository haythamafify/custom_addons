{
    'name': 'App one',
    'version': '1.0',
    'category': 'Learn',
    'summary': 'A brief description of the module',
    'description': 'A more detailed description of the module.',
    'author': 'haytham',
    'website': 'http://yourwebsite.com',
    'license': 'LGPL-3',  # إضافة مفتاح الترخيص هنا
    'depends': ['base', 'sale_management', 'account', 'mail', 'contacts', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/data.xml',
        'views/base_menu.xml',
        'views/building_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_inherit_view.xml',
        'views/tags_view.xml',
        'views/owner_view.xml',
        'views/property_view.xml',
        'views/property_historyview.xml',
        'views/account_move_view.xml',
        'wizard/change_state_wizzard_view.xml',
        'reports/property_report.xml',
        'reports/property_report_report_translatabl.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'app_one/static/src/css/property.css',
            'app_one/static/src/components/listView/listView.js',
            'app_one/static/src/components/listView/listView.css',
            'app_one/static/src/components/listView/listView.xml',

        ],
        'web.assets_frontend': [],
        'web.report.assets_common': ['app_one/static/src/css/font.css'],

    }, 'license': 'LGPL-3',
    'application': True,
}
