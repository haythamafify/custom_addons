{
    'name': 'ACU HR',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'ACU HR  module',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_code_inherit_views.xml',
         'views/education_university_view.xml',
    ],

    'application': True,
}