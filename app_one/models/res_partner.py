from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    # price = fields.Float(compute="_compute_price")

    property_id = fields.Many2one("property")
    price = fields.Float(related = 'property_id.selling_price')



# @api.depends('property_id')
# def _compute_price(self):
#     for rec in self:
#         rec.price = rec.property_id.selling_price
