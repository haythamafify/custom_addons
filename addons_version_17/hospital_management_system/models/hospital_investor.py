from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalInvestor(models.Model):
    _name = 'hospital.investor'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Hospital Investor'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    investment_amount = fields.Float(string="Investment Amount")
