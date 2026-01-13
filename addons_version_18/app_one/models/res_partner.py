from datetime import timedelta

import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"
    property_id = fields.Many2one("property", string="property")
    price = fields.Float(string="price", compute="_compute_price", store=True)

    # The best practise
    # price = fields.Float(string="Price", related="property_id.selling_price", store=True, readonly=True)

    @api.depends("property_id.selling_price")
    def _compute_price(self):
        for rec in self:
            rec.price = rec.property_id.selling_price if rec.property_id else 0.0
