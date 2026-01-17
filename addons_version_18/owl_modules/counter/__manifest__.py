{
    'name': 'Counter OWL Application',
    'version': '18.0.2.0',
    'category': 'Tools',
    'summary': 'Counter and Calculator using OWL framework - Old + New',
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
            # القديم (نسيبه)
            'counter/static/src/components/counter/counter.js',
            'counter/static/src/components/counter/counter.xml',
            'counter/static/src/components/calculator/calculator.js',
            'counter/static/src/components/calculator/calculator.xml',

            # الجديد
            'counter/static/src/components/smart_counter/smart_counter.js',
            'counter/static/src/components/smart_counter/smart_counter.xml',
            'counter/static/src/components/smart_calculator/smart_calculator.js',
            'counter/static/src/components/smart_calculator/smart_calculator.xml',
            'counter/static/src/components/integrated_workspace/integrated_workspace.js',
            'counter/static/src/components/integrated_workspace/integrated_workspace.xml',
            'counter/static/src/components/todo_env/todo_env.js',
            'counter/static/src/components/todo_env/todo_env.xml'
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}