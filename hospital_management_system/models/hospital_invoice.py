# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HospitalInvoice(models.Model):
    _name = 'hospital.invoice'
    _description = 'Hospital Invoice'
    _log_access = True
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'name'

    patient_id = fields.Many2one(
        "hospital.patient",
        string="Patient",
        required=True,
        tracking=True,
        ondelete='cascade'
    )

    appointment_id = fields.Many2one(
        "hospital.appointment",
        string="Appointment",
        required=True,
        tracking=True,
        ondelete='restrict'
    )

    total_amount = fields.Float(
        string="Total Amount",
        required=True,
        tracking=True
    )

    paid_amount = fields.Float(
        string="Paid Amount",
        required=True,
        tracking=True
    )

    remaining_amount = fields.Float(string="Remaining Amount", compute='_compute_remaining_amount', store=True,
                                    tracking=True)

    @api.depends("total_amount", "paid_amount")
    def _compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.total_amount - rec.paid_amount

    payment_status = fields.Selection(
        [('unpaid', 'Unpaid'), ('partial', 'Partially Paid'), ('paid', 'Paid')],
        string="Payment Status",
        compute='_compute_payment_status',
        store=True,
        tracking=True
    )

    invoice_date = fields.Date(
        string="Invoice Date",
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )

    @api.depends('total_amount', 'paid_amount')
    def _compute_payment_status(self):
        for rec in self:
            if rec.paid_amount >= rec.total_amount:
                rec.payment_status = "paid"
            elif rec.paid_amount < rec.total_amount:
                rec.payment_status = "partial"
            else:
                rec.payment_status = "unpaid"

    @api.constrains("total_amount", "paid_amount")
    def _check_total_amount(self):
        for rec in self:
            if rec.paid_amount > rec.total_amount:
                raise ValidationError(_("Paid amount cannot be greater than total amount."))


