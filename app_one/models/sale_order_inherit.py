from odoo import models,fields


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    property_id = fields.Many2one('property')

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        print(" inside SaleOrderInherit ")
        return res
