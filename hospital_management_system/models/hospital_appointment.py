# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Appointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'hospital appointment'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Appointment Name', required=True)

    appointment_date = fields.Datetime(string='Start Time', required=True)

    appointment_time = fields.Float(string='Time', required=True, tracking=True,
                                    help="Example: 13.5 = 1:30 PM")
    medicine_line_ids = fields.One2many('hospital.appointment.medicine.line', 'appointment_id', string='Medicines')
    status = fields.Selection(
        [('new', 'New'), ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('done', 'Done'),
         ('confirm', 'confirm'), ('cancelled', 'Cancelled')], string="Status", default='new', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True,
                                 ondelete='restrict', domain="[('age', '>', 50)]"

                                 )

    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True, tracking=True, )
    room_id = fields.Many2one("hospital.operation.room", "Room", required=True, tracking=True)
    appointment_fees = fields.Float(string='Appointment Fees')
    notes = fields.Text(string="notes")
    symptoms = fields.Text(string=_("Symptoms"), tracking=True)

    chair_rent_fees = fields.Float(string="Chair Rent Fees")
    xray_fees = fields.Float(string="Xray Fees")
    total_price = fields.Float(string='Total Price', store=True, compute='_compute_total_price')
    total_medicine_quantity = fields.Float(string="total medicine", compute="_compute_total_medicine")

    from odoo.exceptions import ValidationError

    def search_for_available_doctor(self):
        for record in self:
            # Debug فقط: طباعة كل الأطباء (اختياري)
            all_doctors = self.env["hospital.doctor"].search([])
            all_doctors_count = self.env["hospital.doctor"].search_count([])
            print("number of doctors ====>", all_doctors_count)
            print("كل الأطباء ====>", all_doctors)
            for doctor in all_doctors:
                print("اسم الدكتور:", doctor.name)
                print("وقت بداية الشيفت:", doctor.available_from)
                print("وقت نهاية الشيفت:", doctor.available_to)

            # البحث عن دكتور متاح وقت الموعد
            available_doctor = self.env['hospital.doctor'].search([
                ('available_from', '<=', record.appointment_time),
                ('available_to', '>=', record.appointment_time)
            ], limit=1)

            print("الأطباء المتاحين ===>", available_doctor)

            if available_doctor:
                first_available_doctor = available_doctor[0]
                print("أول دكتور متاح ===>", first_available_doctor.name)
                record.doctor_id = first_available_doctor.id
                print("✅ تم تخصيص الدكتور:", first_available_doctor.name)
            else:
                raise ValidationError("❌ لا يوجد طبيب متاح في هذا الوقت.")

    @api.depends("medicine_line_ids")
    def _compute_total_medicine(self):
        print("inside _compute_total_medicine ")
        for appointment in self:
            total_qty = 0
            for line in appointment.medicine_line_ids:
                total_qty += line.quantity
            appointment.total_medicine_quantity = total_qty

    @api.depends('appointment_fees', 'xray_fees', 'chair_rent_fees')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.appointment_fees + rec.xray_fees + rec.chair_rent_fees

    medicine_ids = fields.Many2many('hospital.medicine', string='Medicines')

    @api.constrains('start_time', 'end_time')
    def _check_time_validity(self):
        for rec in self:
            if rec.appointment_date and rec.appointment_time and rec.appointment_date >= rec.appointment_time:
                raise ValidationError("End time must be after start time.")

    def print_test(self):
        for rec in self:
            print("self is name", rec.name)
            print("self is date", rec.date)
            print("self is start_time", rec.appointment_date)
            print("self is end_time", rec.appointment_time)

    def action_open_appointment_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("hospital_management_system.action_view_appointment_wizard")
        # action['res_id'] = self.id
        return action

    # status = fields.Selection(
    #     [('new', 'New'), ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('done', 'Done'),
    #      ('cancelled', 'Cancelled')], string="Status", default='new', required=True)

    # Actions to change status
    def action_new(self):
        for record in self:
            record.status = 'new'

    def action_scheduled(self):
        for record in self:
            record.status = 'scheduled'

    def action_confirm(self):
        for record in self:
            record.status = 'confirm'

    def action_in_progress(self):
        for record in self:
            record.status = 'in_progress'

    def action_done(self):
        for record in self:
            record.status = 'done'

    def action_cancelled(self):
        for record in self:
            record.status = 'cancelled'

    def unlink(self):
        for rec in self:
            if rec.status in ["done", "cancelled"]:
                raise ValidationError(_("لا يمكن حذف الموعد لأنه مكتمل أو ملغي."))
        return super(Appointment, self).unlink()

    def get_appointment_id(self):
        appointment = self.env["hospital.appointment"].search([("id", "=", 8)])
        print("appointment id from search function ", appointment.id)
        appointment_browse = self.env["hospital.appointment"].browse(8)
        print("appointment id from browse function ", appointment_browse.id)


@api.onchange("symptoms")
def check_is_doctor(self):
    if not self.env.user.has_group('hospital_management_system.group_staff_doctors'):
        raise ValidationError(_("Only doctors can create symptoms"))
