# -*- coding: utf-8 -*-
{
    'name': "Hospital Management System",

    'summary': "Manage hospital operations: patients, doctors, appointments, labs, and billing.",

    'description': """
Hospital Management System for Odoo
===================================
This module helps manage core hospital functionalities, including:

- Patient registration and medical records
- Doctor and nurse management
- Appointment scheduling
- Hospital departments and operations
- Lab tests and lab appointments
- Hospital admission and surgeries
- Medicine inventory and categories
- Invoicing and reporting
    """,

    'author': "Haytham Afify",
    'website': "https://www.yourcompany.com",

    'category': 'Healthcare',
    'version': '1.0',
    'license': 'LGPL-3',

    # Dependencies
    'depends': ['base', 'mail', 'hr'],

    # Data files
    'data': [
        # Security

        'security/security.xml',
        'security/ir.model.access.csv',
        'wizards/appoint_wizard_view.xml',
        'wizards/appointment_change_doctor_wizard.xml',
        'wizards/new_appointment_wizard_view.xml',


        # Patient & Appointments
        'views/patient_views.xml',
        'views/appointment_view.xml',
        'views/medical_record_view.xml',

        # Staff
        'views/doctor_view.xml',
        'views/users_view.xml',
        'views/hospital_nurse_view.xml',
        'views/hospital_staff_view.xml',

        # Departments & Operations
        'views/department_view.xml',
        'views/hospital_admission_view.xml',
        'views/hospital_operation_room_view.xml',
        'views/hospital_surgery_view.xml',
        'views/room_view.xml',

        # Medicine & Inventory
        'views/medicine_view.xml',
        'views/medicine_category_view.xml',

        # Labs & Reports
        'views/hospital_lab_test_view.xml',
        'views/hospital_lab_appointment_view.xml',
        'views/hospital_monthly_report_view.xml',

        # Invoicing
        'views/hospital_invoice_views.xml',

        # Menus & Templates
        'views/hospital_menus.xml',
        'views/templates.xml',
    ],

    # Demo data (if any)
    'demo': [
        'demo/demo.xml',
    ],

    'icon': '/hospital_management_system/static/description/icon.png',
}
