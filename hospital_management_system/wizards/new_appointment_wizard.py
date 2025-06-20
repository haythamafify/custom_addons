from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class AppointmentWizard(models.TransientModel):
    _name = 'new.appointment.wizard'
    _description = 'New Appointment Wizard'

    name = fields.Char(string='Appointment Name', required=True)
    date = fields.Date(string='Date', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, ondelete='restrict')
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)
    room_id = fields.Many2one("hospital.operation.room", string="Room", required=True)


    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.context.get('default_patient_id'):
            res['patient_id'] = self.env.context.get('default_patient_id')
        return res


    def action_new_appointment_wizard(self):
        # إنشاء السجل الفعلي في hospital.appointment
        self.env['hospital.appointment'].create({
            'name': self.name,
            'date': self.date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'room_id': self.room_id.id,
        })
        return {'type': 'ir.actions.act_window_close'}
