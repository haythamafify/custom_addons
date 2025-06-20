from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class UpdateDoctorAppointmentWizard(models.TransientModel):
    _name = 'update.doctor.wizard'
    _description = 'Update Doctor Appointment Wizard'

    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)

    def action_update_doctor(self):
        # البحث عن كل المواعيد الخاصة بالمريض المحدد
        appointments = self.env['hospital.appointment'].search([
            ('patient_id', '=', self.patient_id.id)
        ])

        if not appointments:
            raise ValidationError(_("No appointments found for this patient."))

        # تحديث الدكتور في كل المواعيد
        appointments.write({'doctor_id': self.doctor_id.id})

        return {'type': 'ir.actions.act_window_close'}
