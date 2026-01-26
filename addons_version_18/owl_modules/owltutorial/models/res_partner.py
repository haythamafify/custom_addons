# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    username = fields.Char(string='User Name')
    expected_salary = fields.Integer(string='Expected Salary')