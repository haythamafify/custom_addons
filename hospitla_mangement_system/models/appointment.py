# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Appointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'hospital appointment'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Appointment Name', required=True)
    date = fields.Date(string='Date', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)
    status = fields.Selection(
        [('new', 'New'),
         ('scheduled', 'Scheduled'),
         ('in_progress', 'In Progress'),
         ('done', 'Done'),
         ('cancelled', 'Cancelled')],
        string="Status",
        default='new',
        required=True)
