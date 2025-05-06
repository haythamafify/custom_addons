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

    def print_test(self):
        for rec in self:
            print("self is name", rec.name )
            print("self is date", rec.date )
            print("self is start_time", rec.start_time )
            print("self is end_time", rec.end_time )


