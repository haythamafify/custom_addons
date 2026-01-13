from datetime import timedelta

import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Clients(models.Model):
    _name = "clients"
    _description = 'Clients Management'
    _inherit = "owner"
