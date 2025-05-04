{
    'name': 'ACU HR',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'ACU HR  module',
    'depends': ['base', 'hr', 'hr_attendance_sheet', 'hr_payroll_community'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_code_inherit_views.xml',
        'views/education_university_view.xml',
    ],

    'application': True,
}
