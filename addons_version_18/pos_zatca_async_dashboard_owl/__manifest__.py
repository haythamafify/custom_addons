{
    'name': 'POS ZATCA Async - Fix Concurrency',
    'version': '18.0.1.0.0',
    'summary': 'Decouple ZATCA EDI chain index from POS transaction to fix SerializationFailure',
    'description': """
        Problem:
        --------
        Under high load in POS (restaurant), multiple simultaneous orders
        cause a psycopg2.errors.SerializationFailure because the ZATCA
        chain_index sequence uses FOR UPDATE NOWAIT inside the POS transaction.

        Solution:
        ---------
        This module decouples the ZATCA EDI processing (chain index + submission)
        from the POS order transaction by:
        1. Overriding _generate_pos_order_invoice to skip synchronous ZATCA
        2. A scheduled action (cron) picks up pending EDI documents and processes them async
        3. A retry mechanism handles transient failures gracefully
    """,
    'author': 'Haytham Afify',
    'website': 'https://github.com/haythamafify/',
    'linkedin': 'https://www.linkedin.com/in/haytham-gamal-4165797a/',
    'category': 'Point of Sale',
    'images': [
        'static/description/icon.png',
    ],
    'depends': [
        'point_of_sale',
        'account',
        'l10n_sa_edi',

    ],
  'data': [
    'security/ir.model.access.csv',
    'data/ir_cron.xml',
    'data/zatca_sync_monitor_data.xml',
    'views/zatca_sync_monitor_views.xml',
    'views/zatca_dashboard_action.xml',
],
'assets': {
    'web.assets_backend': [
        'pos_zatca_async_dashboard_owl/static/src/js/zatca_dashboard.js',
        'pos_zatca_async_dashboard_owl/static/src/xml/zatca_dashboard.xml',
    ],
},
   
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
