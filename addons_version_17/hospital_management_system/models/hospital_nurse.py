from odoo import models, fields

class HospitalNurse(models.Model):
    _name = 'hospital.nurse'
    _description = 'Hospital Nurse'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Nurse Name', required=True)
    department_id = fields.Many2one('hospital.department', string='Department', required=True)
    shift_start = fields.Datetime(string='Shift Start', required=True)
    shift_end = fields.Datetime(string='Shift End', required=True)
    mobile = fields.Char(string='Mobile Number', required=True)
    assigned_patients = fields.One2many('hospital.patient', 'nurse_id', string='Assigned Patients')
