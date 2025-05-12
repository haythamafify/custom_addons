# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HospitalLabTest(models.Model):
    _name = 'hospital.lab.test'
    _description = 'Hospital Lab Test'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_type = fields.Selection([
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('other', 'Other'),
    ], string='Test Type', required=True, tracking=True)

    test_date = fields.Datetime(string='Test Date', default=fields.Datetime.now, required=True, tracking=True)
    result = fields.Text(string='Test Result')
    doctor_id = fields.Many2one('hospital.doctor', string='Requested By Doctor')
