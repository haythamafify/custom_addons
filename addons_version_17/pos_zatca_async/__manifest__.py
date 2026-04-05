{
    'name': 'POS ZATCA Async - Fix Concurrency',
    'version': '17.0.1.0.0',
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
    'author': 'Custom',
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
        'l10n_sa_edi',
        'account_edi',
    ],
    'data': [
        'data/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
