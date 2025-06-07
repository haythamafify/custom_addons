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
    date = fields.Date(string='Date', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)
    medicine_line_ids = fields.One2many('hospital.appointment.medicine.line', 'appointment_id', string='Medicines')
    status = fields.Selection(
        [('new', 'New'), ('scheduled', 'Scheduled'), ('in_progress', 'In Progress'), ('done', 'Done'),
         ('confirm', 'confirm'), ('cancelled', 'Cancelled')], string="Status", default='new', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True,
                                 ondelete='restrict', domain="[('age', '>', 50)]"

                                 )

    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True, tracking=True, )
    room_id = fields.Many2one("hospital.operation.room", "Room", required=True, tracking=True)
    appointment_fees = fields.Float(string='Appointment Fees', required=True)
    notes = fields.Text(string="notes")
    symptoms = fields.Text(string=_("Symptoms"), tracking=True)

    chair_rent_fees = fields.Float(string="Chair Rent Fees")
    xray_fees = fields.Float(string="Xray Fees")
    total_price = fields.Float(string='Total Price', store=True, compute='_compute_total_price')
    total_medicine_quantity = fields.Float(string="total medicine", compute="_compute_total_medicine")

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
            if rec.start_time and rec.end_time and rec.start_time >= rec.end_time:
                raise ValidationError("End time must be after start time.")

    def print_test(self):
        for rec in self:
            print("self is name", rec.name)
            print("self is date", rec.date)
            print("self is start_time", rec.start_time)
            print("self is end_time", rec.end_time)

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


    @api.onchange("symptoms")
    def check_is_doctor(self):
        if not self.env.user.has_group('hospital_management_system.group_staff_doctors'):
            raise ValidationError(_("Only doctors can create symptoms"))

