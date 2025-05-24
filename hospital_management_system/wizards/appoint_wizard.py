from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta


class AppointmentWizard(models.TransientModel):
    _name = 'appointment.wizard'
    _description = 'Appointment Wizard'



    name  = fields.Char(string = 'Name', readonly=False, store=True)


    def action_print_test(self):
        active_id = self.env.context.get('active_id')
        print ("active_id ---> ", active_id)
        appointment = self.env['hospital.appointment'].search([('id', '=', active_id)])
        print ("------------------------------")
        print ("appointment.id ---> ", appointment.id)
        print ("appointment.patient_id ---> ", appointment.patient_id)
        print ("appointment.doctor_id ---> ", appointment.doctor_id)
        print ("------------------------------")

        appointment.notes = self.name


        print ("test")
