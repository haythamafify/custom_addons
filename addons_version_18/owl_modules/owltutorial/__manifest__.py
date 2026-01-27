{
    'name': 'OWL Tutorial',
    'version': '18.0.1.0',
    'category': 'Tools',
    'summary': 'Simple Todo List using OWL framework + Bootstrap 5',
    'author': 'Haytham Gamal',
    'website': 'https://github.com/haythamafify/custom_addons',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail', 
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/to_do_list_view.xml',
        'views/res_partner_view.xml',
        'views/odoo_services.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            # Bootstrap 5 CSS (قبل الـ components)
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css',
            
            # OWL Components
            'owltutorial/static/src/components/**/*.js',
            'owltutorial/static/src/components/**/*.xml',
            'owltutorial/static/src/components/**/*.scss',
            
            # Bootstrap Icons
            'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
            
            # Bootstrap 5 JS Bundle (بعد الـ components)
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
