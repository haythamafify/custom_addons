# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-

from odoo import models, fields


class HospitalLabAppointment(models.Model):
    _name = 'hospital.lab.appointment'  # Model name

    _description = 'Hospital Lab Appointment'  # Model description
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Field definitions
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_type = fields.Selection([
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('xray', 'X-ray'),
    ], string='Test Type', required=True)
    appointment_date = fields.Date(string='Appointment Date', required=True)
    status = fields.Selection([
        ('new', 'New'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='new', required=True)
    lab_technician_id = fields.Many2one('hr.employee', string='Lab Technician', required=True)