{
    'name': 'To Do App',
    'version': '1.0',
    'category': 'Productivity',
    'author': 'haytham',
    'website': 'http://www.yourcompany.com',

    'depends': ['base','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/base_menu_view.xml',
        'views/todo_task_view.xml',

    ],

    'application': True,

}
