from odoo import models, fields

class HospitalSurgery(models.Model):
    _name = 'hospital.surgery'
    _description = 'Hospital Surgery'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    room_id = fields.Many2one('hospital.operation.room', string='Operation Room')
    scheduled_time = fields.Datetime(string='Scheduled Time', required=True, default=fields.Datetime.now)
    surgery_type = fields.Selection([
        ('minor', 'Minor Surgery'),
        ('major', 'Major Surgery'),
        ('emergency', 'Emergency Surgery'),
        ('other', 'Other'),
    ], string='Surgery Type', required=True)
    status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='scheduled', tracking=True)
    notes = fields.Text(string='Notes')
