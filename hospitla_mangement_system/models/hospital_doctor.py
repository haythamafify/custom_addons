# -*- coding: utf-8 -*-

import re
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Doctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'doctor'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    specialization = fields.Char(string='Specialization', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    available_from = fields.Datetime(string='Available From', tracking=True)
    available_to = fields.Datetime(string='Available To', tracking=True)
    is_available = fields.Boolean(string='Is Available', default=True, tracking=True)
