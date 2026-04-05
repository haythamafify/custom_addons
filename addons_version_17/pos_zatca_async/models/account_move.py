import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

# How many invoices to process per cron run (avoid timeout)
BATCH_SIZE = 50


class AccountMoveSend(models.TransientModel):
    """
    Intercept the ZATCA web service call when triggered from POS context.
    Instead of calling ZATCA synchronously, we let the invoice save
    and mark the EDI document as pending — cron picks it up later.
    """

    _inherit = 'account.move.send'

    def _call_web_service_before_invoice_pdf_render(self, invoices_data_web_service):
        """
        If we are inside a POS transaction (skip_zatca_edi_sync context),
        skip the synchronous ZATCA call entirely.
        The EDI documents stay in state 'to_send' and the cron will process them.
        """
        if self.env.context.get('skip_zatca_edi_sync'):
            _logger.info(
                "ZATCA async: skipping synchronous EDI for %d invoice(s) — "
                "will be processed by cron.",
                len(invoices_data_web_service),
            )
            # Do NOT call super — skip ZATCA web service entirely here
            return

        return super()._call_web_service_before_invoice_pdf_render(
            invoices_data_web_service
        )


class AccountMove(models.Model):
    """
    Cron-based async ZATCA processor.

    Flow:
        POS closes order
            └── invoice created (EDI doc state = 'to_send')
                    └── [cron runs every N minutes]
                            └── picks pending EDI docs
                                    └── processes them one-by-one (sequential)
                                            └── chain_index assigned safely (no concurrency)
    """

    _inherit = 'account.move'

    @api.model
    def _cron_process_zatca_edi(self):
        """
        Cron entry point.
        Finds invoices with pending ZATCA EDI documents and processes them
        sequentially to avoid any sequence/chain_index collision.
        """
        _logger.info("ZATCA async cron: starting run.")

        # Find EDI documents pending for ZATCA (l10n_sa_edi format)
        pending_docs = self.env['account.edi.document'].search([
            ('state', 'in', ('to_send', 'to_cancel')),
            ('edi_format_id.code', '=', 'sa_zatca'),
            ('move_id.move_type', 'in', ('out_invoice', 'out_refund')),
        ], limit=BATCH_SIZE, order='id asc')

        if not pending_docs:
            _logger.info("ZATCA async cron: no pending documents found.")
            return

        _logger.info(
            "ZATCA async cron: found %d pending EDI document(s).",
            len(pending_docs),
        )

        # Process sequentially — one at a time — this is THE KEY
        # that eliminates the SerializationFailure: no two chain_index
        # assignments happen concurrently anymore.
        success = 0
        errors = 0
        for doc in pending_docs:
            try:
                # Each doc gets its own savepoint so a single failure
                # doesn't roll back the whole batch
                with self.env.cr.savepoint():
                    doc._process_documents_web_services(with_commit=False)
                    success += 1
            except Exception as e:
                errors += 1
                _logger.error(
                    "ZATCA async cron: failed to process EDI doc id=%s "
                    "for invoice %s. Error: %s",
                    doc.id,
                    doc.move_id.name,
                    str(e),
                )
                # Continue with the rest — don't stop the whole batch

        _logger.info(
            "ZATCA async cron: finished. success=%d errors=%d",
            success,
            errors,
        )
