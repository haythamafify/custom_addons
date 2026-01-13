from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AppointmentChangeDoctorWizard(models.TransientModel):
    _name = 'appointment.change.doctor.wizard'
    _description = 'Wizard to Change Doctor in Appointment'

    doctor_id = fields.Many2one('hospital.doctor', string='New Doctor', required=True)

    def action_change_doctor(self):
        # الحصول على ID للسجل المفتوح حالياً
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise UserError(_("No appointment record found."))

        # البحث عن السجل المطلوب
        appointment = self.env['hospital.appointment'].browse(active_id)
        if not appointment.exists():
            raise UserError(_("Appointment not found."))

        # تغيير الطبيب
        appointment.doctor_id = self.doctor_id.id

        # إغلاق النافذة بعد تنفيذ العملية
        return {'type': 'ir.actions.act_window_close'}
