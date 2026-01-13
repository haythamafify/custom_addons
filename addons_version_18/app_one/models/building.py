from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Building(models.Model):
    _name = "building"
    _description = "Building Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Building Name', required=True, tracking=True)
    no = fields.Integer(string='Building Number', required=True, tracking=True)
    code = fields.Char(string='Building Code', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True, translate=True)
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('unique_building_no', 'unique(no)', 'Building number must be unique!'),
        ('unique_building_code', 'unique(code)', 'Building code already exists!'),
    ]

    @api.constrains('no')
    def _check_building_no(self):
        for record in self:
            if record.no <= 0:
                raise ValidationError(_('Building number must be greater than zero!'))

    def name_get(self):
        """تخصيص اسم العرض ليظهر: [Code] Name"""
        result = []
        for record in self:
            name = f'[{record.code}] {record.name}'
            result.append((record.id, name))
        return result
