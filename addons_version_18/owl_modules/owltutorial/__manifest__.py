{
    'name': 'OWL Tutorial',
    'version': '18.0.1.0',
    'category': 'Tools',
    'summary': 'Simple Todo List using OWL framework',
    'author': 'Haytham Gamal',
    'website': 'https://github.com/haythamafify/custom_addons',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
         'mail', 
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/to_do_list_view.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
                 'owltutorial/static/src/components/**/*.js',
        'owltutorial/static/src/components/**/*.xml',
        'owltutorial/static/src/components/**/*.scss', 
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
