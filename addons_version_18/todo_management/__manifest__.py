{
    'name': 'Todo Management',
    'version': '18.0.1.0',
    'category': 'Productivity',
    'summary': 'Manage daily tasks with workflow and chatter',
    'description': """
Todo Management System
======================
Features:
* Create and manage tasks
* Assign tasks to users
* Task state workflow
* Due dates tracking
* Chatter integration
    """,
    'author': 'Haytham Gamal',
    'website': 'https://github.com/haytham/todo-management',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/todo_task_view.xml',
        'views/base_menu_view.xml',

    ],
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
