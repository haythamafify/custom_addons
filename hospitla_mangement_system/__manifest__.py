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
    'depends': ['base', 'mail', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/patient_views.xml',
        'views/appointment_view.xml',
        'views/medicine_view.xml',
        'views/templates.xml',
        'views/doctor_view.xml',
        'views/department_view.xml',
        'views/medical_record_view.xml',
        'views/hospital_invoice_views.xml',
        'views/medicine_category_view.xml',
        'views/hospital_admission_view.xml',
        'views/hospital_lab_test_view.xml',
        'views/hospital_operation_room_view.xml',
        'views/hospital_surgery_view.xml',
        'views/hospital_nurse_view.xml',
        'views/hospital_staff_view.xml',
        'views/hospital_lab_appointment_view.xml',
        'views/hospital_monthly_report_view.xml',

        'views/hospital_menus.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'icon': '/hospital_management_system/static/description/icon.png',
'license': 'LGPL-3',
}
