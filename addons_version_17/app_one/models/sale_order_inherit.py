from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    property_id = fields.Many2one('property')
    total_discount = fields.Float(
        string='Total Discount',
        compute='_compute_total_discount',
        store=True  # مهم لو هتستخدم الحقل في التقارير أو الفيو
    )

    @api.depends('order_line.price_unit', 'order_line.product_uom_qty', 'order_line.discount')
    def _compute_total_discount(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                if line.discount:
                    line_discount = line.price_unit * line.product_uom_qty * line.discount / 100
                    total += line_discount
            order.total_discount = total

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        print(" inside SaleOrderInherit ")
        return res
