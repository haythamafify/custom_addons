# -*- coding: utf-8 -*-

import re
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Medicine(models.Model):
    _name = 'hospital.medicine'
    _description = 'medicine'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Medicine Name', required=True, tracking=True)
    category_id = fields.Many2one('hospital.medicine.category', string='Category', tracking=True)
    price = fields.Float(string='Price', tracking=True)
    quantity = fields.Integer(string='Quantity', tracking=True)
    expiry_date = fields.Date(string='Expiry Date', tracking=True)

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        for record in self:
            if record.expiry_date and record.expiry_date < fields.Date.today():
                raise ValidationError("The expiry date must be in the future!")
