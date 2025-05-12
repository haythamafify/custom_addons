# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MedicalRecord(models.Model):
    _name = 'hospital.medical.record'
    _description = 'Medical Record'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # الحقول
    name = fields.Char(string='Name', required=True, tracking=True)
    patient_id = fields.Many2one("hospital.patient", string="Patient", required=True, tracking=True)

    diagnosis = fields.Text(string="Diagnosis", required=True, tracking=True)

    prescription = fields.Text(string="Prescription", required=True, tracking=True)

    record_date = fields.Date(
        string="Record Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )

    doctor_id = fields.Many2one("hospital.doctor", string="Doctor", required=True, tracking=True)
