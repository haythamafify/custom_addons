from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class Room(models.Model):
    _name = 'hospital.room'
    _description = 'Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Room Number/Name', required=True, tracking=True)
    department_id = fields.Many2one('hospital.department', string='Department', tracking=True)
    bed_count = fields.Integer(string='Total Beds', default=1)
    occupied_bed_count = fields.Integer(string='Occupied Beds')

    state = fields.Selection([
        ('available', 'Available'),
        ('full', 'Full'),
        ('maintenance', 'Maintenance')
    ], string='Status', default='available', tracking=True)
