import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

# How many invoices to process per cron run (avoid timeout)
BATCH_SIZE = 50

ZATCA_EDI_STATE_PARAM = 'pos_zatca_async_v18.zatca_edi_state_field'


class AccountMoveSend(models.AbstractModel):
    """
    Odoo 18: account.move.send is an AbstractModel (not TransientModel anymore).
    We inherit it the same way to intercept _call_web_service_before_invoice_pdf_render.
    """

    _inherit = 'account.move.send'

    def _call_web_service_before_invoice_pdf_render(self, invoices_data_web_service):
        """
        If triggered from POS context, skip synchronous ZATCA call.
        Invoices stay in 'to_send' state — cron picks them up.
        """
        if self.env.context.get('skip_zatca_edi_sync'):
            _logger.info(
                "ZATCA async [v18]: skipping synchronous EDI for %d invoice(s) — "
                "will be processed by cron.",
                len(invoices_data_web_service),
            )
            return  # skip — do NOT call super

        return super()._call_web_service_before_invoice_pdf_render(
            invoices_data_web_service
        )


class AccountMove(models.Model):
    """
    Odoo 18 async ZATCA cron processor.

    In v18, account.edi.document is REMOVED.
    EDI state is tracked directly on account.move via:
        - move.l10n_sa_edi_state  (field on the invoice)
    """

    _inherit = 'account.move'

    zatca_edi_state_display = fields.Char(
        compute='_compute_zatca_edi_state_display'
    )

    @api.model
    def _get_zatca_edi_state_field_name(self):
        configured = self.env['ir.config_parameter'].sudo().get_param(ZATCA_EDI_STATE_PARAM)
        if configured:
            configured = configured.strip()
            if configured in self._fields:
                return configured
            _logger.warning(
                "ZATCA async [v18]: configured EDI state field '%s' not found on account.move.",
                configured,
            )

        candidates = [
            'l10n_sa_edi_state',
            'l10n_sa_zatca_state',
            'l10n_sa_state',
            'edi_state',
        ]
        for name in candidates:
            if name in self._fields:
                return name

        for name in self._fields:
            if name.startswith('l10n_sa_') and 'state' in name:
                return name

        return False

    def _compute_zatca_edi_state_display(self):
        state_field = self._get_zatca_edi_state_field_name()
        for move in self:
            move.zatca_edi_state_display = (getattr(move, state_field) if state_field else False) or False

    @api.model
    def _cron_process_zatca_edi(self):
        """
        Cron entry point for Odoo 18.

        Finds posted invoices where ZATCA EDI is still pending
        and processes them sequentially (one at a time) to guarantee
        no chain_index collision.
        """
        _logger.info("ZATCA async cron [v18]: starting run.")

        state_field = self._get_zatca_edi_state_field_name()
        if not state_field:
            _logger.warning(
                "ZATCA async cron [v18]: could not find ZATCA EDI state field on account.move. Skipping run."
            )
            return

        # In v18 l10n_sa_edi, the invoice has l10n_sa_edi_state field:
        # 'to_send'  → ready to submit but not yet sent
        # 'error'    → previous attempt failed (retry)
        pending_invoices = self.search([
            ('state', '=', 'posted'),
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            (state_field, 'in', ('to_send', 'error')),
        ], limit=BATCH_SIZE, order='id asc')

        if not pending_invoices:
            _logger.info("ZATCA async cron [v18]: no pending invoices found.")
            return

        _logger.info(
            "ZATCA async cron [v18]: found %d pending invoice(s).",
            len(pending_invoices),
        )

        success = 0
        errors = 0

        # Process ONE BY ONE — this is the critical part.
        # Sequential processing = no concurrent chain_index assignment = no lock collision.
        for invoice in pending_invoices:
            try:
                with self.env.cr.savepoint():
                    # v18: trigger EDI via action_process_edi_web_services
                    # which calls _l10n_sa_post_zatca_edi internally
                    invoice.action_process_edi_web_services()
                    success += 1
                    _logger.info(
                        "ZATCA async cron [v18]: invoice %s submitted OK.",
                        invoice.name,
                    )
            except Exception as e:
                errors += 1
                _logger.error(
                    "ZATCA async cron [v18]: failed invoice %s (id=%s). Error: %s",
                    invoice.name,
                    invoice.id,
                    str(e),
                )

        _logger.info(
            "ZATCA async cron [v18]: done. success=%d  errors=%d",
            success,
            errors,
        )
