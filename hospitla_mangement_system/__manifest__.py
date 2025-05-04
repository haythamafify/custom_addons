# -*- coding: utf-8 -*-
{
    'name': "hospitla_mangement_system",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Simple Hospital Management System
    """,

    'author': "Haytham Afify",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Helath Care',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/patient_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

