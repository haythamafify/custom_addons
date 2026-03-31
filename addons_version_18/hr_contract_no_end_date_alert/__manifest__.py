# -*- coding: utf-8 -*-
{
    'name': 'HR Contract No End Date Alert',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Show warning when HR contract has no end date',
    'author': 'Haytham Afify',
    'website': 'https://github.com/haythamafify',
    'license': 'LGPL-3',
    'depends': [
        'hr_contract',
        'web',
    ],
    'data': [
        'views/hr_contract_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hr_contract_no_end_date_alert/static/src/js/hr_contract_form.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
