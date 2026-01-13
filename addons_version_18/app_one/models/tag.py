from datetime import timedelta

import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Tag(models.Model):
    _name = "tag"
    _description = "tag"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _log_access = True


    name = fields.Char(required=True)
