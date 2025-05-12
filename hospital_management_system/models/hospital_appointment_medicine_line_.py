# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HospitalAppointmentMedicineLine(models.Model):
    _name = 'hospital.appointment.medicine.line'
    _description = 'Medicine Line'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    medicine_id = fields.Many2one(
        "hospital.medicine",
        string="Medicine",
        required=True,
        tracking=True
    )
    quantity = fields.Float(string="Quantity", digit=("20", "2"), required=True, tracking=True)
    dose_per_day = fields.Float(string="Dosage", required=True, tracking=True)
    appointment_id = fields.Many2one("hospital.appointment", string="Appointment", required=True, tracking=True)
