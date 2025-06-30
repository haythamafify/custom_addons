# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Doctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'doctor'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True, tracking=True)
    license_number = fields.Char(string='License Number', required=True, tracking=True)
    specialization = fields.Char(string='Specialization', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    department_id = fields.Many2one('hospital.department', string='Department', tracking=True)
    available_from = fields.Float(string='Available From (HH.MM)', help="Example: 9.5 means 9:30 AM")
    available_to = fields.Float(string='Available To (HH.MM)', help="Example: 17.0 means 5:00 PM")
    is_available = fields.Boolean(string='Is Available', default=True, tracking=True)
    image = fields.Binary(string="Doctor Image")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if args is None:
            args = []

        # البحث في 3 حقول: الاسم، رقم الرخصة، والموبايل
        domain = args + [
            '|', '|',
            ('name', operator, name),
            ('license_number', operator, name),
            ('mobile', operator, name)
        ]

        records = self.search(domain, limit=limit)
        return records.name_get()

    def name_get(self):
        result = []
        for record in self:
            # عرض الاسم مع رقم الموبايل
            name = record.name
            if record.mobile:
                name = f"{record.name} - {record.mobile}"

            result.append((record.id, name))

        return result
