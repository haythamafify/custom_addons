{
    'name': 'Counter OWL Application',
    'version': '18.0.2.0',
    'category': 'Tools',
    'summary': 'Counter and Calculator using OWL framework - Old + New + Services',
    'author': 'Haytham Gamal',
    'website': 'https://github.com/haythamafify/custom_addons/tree/main/addons_version_18/owl_modules/counter',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'crm',
        'sale',
        'stock',
        'stock_barcode',
    ],
    'data': [
        'views/counter_menu.xml',
        'views/stock_picking_views.xml',
    ],
    'demo': [],
    'assets': {
        'web.assets_backend': [
            # SERVICES FIRST
            'counter/static/src/services/counter_service.js',
            'counter/static/src/services/weather_service.js',
            'counter/static/src/services/orm_service.js',

            # OLD COMPONENTS
            'counter/static/src/components/counter/counter.js',
            'counter/static/src/components/counter/counter.xml',
            'counter/static/src/components/calculator/calculator.js',
            'counter/static/src/components/calculator/calculator.xml',

            # SERVICE COMPONENTS
            'counter/static/src/components/counter_service/counter_with_service.js',
            'counter/static/src/components/counter_service/counter_with_service.xml',
            'counter/static/src/components/weather/weather_component.js',
            'counter/static/src/components/weather/weather_component.xml',

            # NEW COMPONENTS
            'counter/static/src/components/smart_counter/smart_counter.js',
            'counter/static/src/components/smart_counter/smart_counter.xml',
            'counter/static/src/components/smart_calculator/smart_calculator.js',
            'counter/static/src/components/smart_calculator/smart_calculator.xml',
            'counter/static/src/components/integrated_workspace/integrated_workspace.js',
            'counter/static/src/components/integrated_workspace/integrated_workspace.xml',
            'counter/static/src/components/todo_env/todo_env.js',
            'counter/static/src/components/todo_env/todo_env.xml',
            
            # CRM LEAD CREATOR
            'counter/static/src/components/crm_lead_creator/crm_lead_creator.js',
            'counter/static/src/components/crm_lead_creator/crm_lead_creator.xml',
            
            # SALE ORDER LEAD TRACKER
            'counter/static/src/components/sale_order_lead_tracker/sale_order_lead_tracker.js',
            'counter/static/src/components/sale_order_lead_tracker/sale_order_lead_tracker.xml',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}