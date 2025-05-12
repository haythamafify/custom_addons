from odoo import models, fields


class HospitalAdmission(models.Model):
    _name = 'hospital.admission'
    _description = 'Hospital Admission'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_date = fields.Datetime(string='Admission Date', default=fields.Datetime.now, required=True)
    discharge_date = fields.Datetime(string='Discharge Date')
    room_number = fields.Char(string='Room Number')
    reason = fields.Text(string='Reason for Admission')
