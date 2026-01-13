from odoo import models, fields

class HospitalStaff(models.Model):
    _inherit = 'hr.employee'
    _log_access = True
    _rec_name = 'name'

    role_in_hospital = fields.Selection([
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Administrator'),
        ('other', 'Other'),
    ], string='Role in Hospital', required=True)

    hospital_department_id = fields.Many2one(
        'hospital.department',
        string='Hospital Department',
        required=True
    )

    shift_type = fields.Selection([
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ], string='Shift Type', required=True)

    is_active_medical_staff = fields.Boolean(
        string='Active Medical Staff',
        default=True
    )