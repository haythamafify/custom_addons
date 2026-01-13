from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class Users(models.Model):
    _inherit = 'res.users'

    doctor_id = fields.Many2one('hospital.doctor', string = 'Related Doctor')
