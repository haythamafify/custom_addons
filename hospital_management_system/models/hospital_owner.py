from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalOwner(models.Model):
    _name = 'hospital.owner'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Hospital Owner'

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
