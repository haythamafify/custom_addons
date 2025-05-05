# -*- coding: utf-8 -*-
{
    'name': "hospital_management_system",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Simple Hospital Management System
    """,

    'author': "Haytham Afify",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Health Care',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hospital_menus.xml',
        'views/patient_views.xml',
        'views/appointment_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
'icon': '/hospital_management_system/static/description/icon.png'
}
