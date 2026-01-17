{
    'name': 'Counter OWL Application',
    'version': '18.0.1.0',
    'category': 'Tools',
    'summary': 'Simple Counter application using OWL framework',
    'author': 'Haytham Gamal',
    'website': 'https://github.com/haythamafify/custom_addons/tree/main/addons_version_18/owl_modules/counter',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'views/counter_menu.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            'counter/static/src/components/counter/counter.js',
            'counter/static/src/components/counter/counter.xml',
            'counter/static/src/components/calculator/calculator.js',
            'counter/static/src/components/calculator/calculator.xml',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
