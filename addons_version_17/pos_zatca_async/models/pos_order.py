import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    """
    Override _generate_pos_order_invoice to skip synchronous ZATCA processing.

    ROOT CAUSE:
        _process_saved_order()
            └── _generate_pos_order_invoice()               ← inside POS transaction
                    └── _generate_pdf_and_send_invoice()
                            └── _call_web_service_before_invoice_pdf_render()
                                    └── action_process_edi_web_services()
                                            └── _l10n_sa_post_zatca_edi()
                                                    └── _l10n_sa_edi_get_next_chain_index()
                                                            └── ir.sequence (FOR UPDATE NOWAIT) 💥

    FIX:
        POS Transaction:   create order + invoice (no ZATCA)  ✅ fast, no lock
        Background Cron:   chain_index + ZATCA submission      ✅ sequential, no collision
    """

    _inherit = 'pos.order'

    def _generate_pos_order_invoice(self):
        """
        Override to generate the invoice but skip synchronous ZATCA EDI.
        ZATCA will be processed asynchronously by the cron job.
        """
        # Call super but with context flag to skip ZATCA web service call
        return super(PosOrder, self.with_context(
            skip_zatca_edi_sync=True
        ))._generate_pos_order_invoice()
