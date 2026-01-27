# -*- coding: utf-8 -*-
from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_set_quantities_to_demand(self):
        """
        Set qty_done = product_uom_qty for all move lines
        """
        for move_line in self.move_line_ids:
            if move_line.product_uom_qty > 0:
                move_line.qty_done = move_line.product_uom_qty
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'All quantities have been set to their demand values.',
                'type': 'success',
                'sticky': False,
            }
        }