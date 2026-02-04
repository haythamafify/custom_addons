{
    'name': 'web_portal',
    'version': '18.0.1.0.0',
    'category': 'Website/Portal',
    'summary': 'Learning Odoo 18 Portal',
    'author': 'Haytham Gamal',
    'license': 'LGPL-3',

    'depends': [
        'base',
        'portal',
        'app_one',
    ],

    'data': [
        'views/portal_templates.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            # Bootstrap 5
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css',
            'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
            'https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js',

            # OWL Components
            'web_portal/static/src/components/**/*.js',
            'web_portal/static/src/components/**/*.xml',
            'web_portal/static/src/components/**/*.css',
        ],
    },

    'application': True,
    'installable': True,
}
