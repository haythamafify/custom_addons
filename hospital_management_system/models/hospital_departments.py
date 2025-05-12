# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Department(models.Model):
    _name = 'hospital.department'
    _description = 'Hospital Department'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)

    responsible_doctor_id = fields.Many2one('hospital.doctor', string='Responsible Doctor', tracking=True)
