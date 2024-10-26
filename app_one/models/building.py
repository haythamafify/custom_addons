from email.policy import default

from odoo import models, fields


class Building(models.Model):
    _name = "building"
    _description = "Building Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = "code"

    no = fields.Integer(string="Building Number", tracking=True)
    code = fields.Char(string="Building Code", required=True, tracking=True)
    description = fields.Text(string="Description", tracking=True)
    location = fields.Char(string="Location", tracking=True)
    owner = fields.Many2one('res.partner', string="Owner", tracking=True)
    is_active = fields.Boolean(string="Is Active", default=True, tracking=True)
    name = fields.Char()
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ('unique_building_number', 'UNIQUE(no)', 'The building number must be unique.')
    ]
